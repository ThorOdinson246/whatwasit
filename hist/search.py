"""Semantic query search over indexed shell history sessions.

Ties together the embedder, vector index, and SQLite store: a query string is
embedded, the nearest session vectors are looked up, and each matched
session's commands are individually re-ranked against the query so the
output layer can highlight which specific commands made the session relevant.
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

import numpy as np

from .config import Config
from .embedder import build_embedder
from .index import build_index
from .interfaces import Embedder, VectorIndex
from . import db
from .models import SearchResult

MAX_MATCHED_INDICES = 3
MATCH_SCORE_MARGIN = 0.05

# Pivoted length normalization (BM25-style).
# Documents shorter than _LN_PIVOT chars get a mild boost; longer ones get a
# mild penalty.  _LN_SLOPE=0 disables the adjustment entirely; _LN_SLOPE=1
# applies the maximum correction.  0.4 is a conservative midpoint that
# prevents noisy long sessions from dominating without over-penalizing
# genuinely rich sessions.
_LN_SLOPE: float = 0.4
_LN_PIVOT: float = 175.0


# ---------------------------------------------------------------------------
# Hybrid search: Reciprocal Rank Fusion (RRF) of semantic + keyword signals.
#
# RRF is chosen over a weighted linear sum because it requires no score
# calibration between the two signals (cosine similarity vs. Jaccard
# overlap have different dynamic ranges).  The single tunable constant k=60
# is the standard literature value; it dampens the influence of top-ranked
# results so neither signal dominates.
#
# The keyword scorer runs over the semantic candidates already retrieved from
# the ANN index, so no separate keyword index is needed.  For production
# indexes, set top_k high enough (or use a "recall budget") so that
# keyword-specific sessions are included in the candidate set.
# ---------------------------------------------------------------------------
_RRF_K = 60
_KW_TOKEN_RE = re.compile(r"[a-z0-9_.-]+")

# Only activate the keyword signal when at least one candidate session
# reaches this Jaccard score against the query.  Intent-paraphrase queries
# (which avoid tool names) produce scores near 0; exact-keyword queries
# (tool names, flags, error codes) easily exceed this threshold.
# Value chosen empirically: intent queries score < 0.04; keyword queries > 0.08.
_HYBRID_KW_MIN_SCORE: float = 0.20


def _strip_hints(doc_text: str) -> str:
    """Return doc_text without the semantic hint expansion line.

    The "context: ..." line added by Session.to_document() is useful for
    semantic embeddings but must NOT be used for keyword scoring: its
    natural-language phrases create spurious overlap with intent-paraphrase
    queries, breaking the separation between the two signals.
    """
    return "\n".join(
        line for line in doc_text.split("\n") if not line.startswith("context: ")
    )


def _keyword_score(query: str, doc_text: str) -> float:
    """Jaccard token-overlap similarity between query and raw command text.

    Uses only the raw-command portion of doc_text (hints stripped) so that
    the keyword signal reflects actual command/flag/tool-name presence rather
    than the natural-language expansions added for semantic search.
    """
    raw  = _strip_hints(doc_text)
    qtoks = set(_KW_TOKEN_RE.findall(query.lower()))
    dtoks = set(_KW_TOKEN_RE.findall(raw.lower()))
    if not qtoks or not dtoks:
        return 0.0
    inter = len(qtoks & dtoks)
    union = len(qtoks | dtoks)
    return inter / union if union > 0 else 0.0


def _rrf_merge(
    sem_ranked: List[Tuple[int, float]],
    kw_ranked: List[Tuple[int, float]],
    k: int = _RRF_K,
) -> List[Tuple[int, float]]:
    """Merge two ranked lists via Reciprocal Rank Fusion.

    Each list is a sequence of *(session_id, score)* pairs already sorted
    best-first.  Returns a new list of *(session_id, rrf_score)* sorted by
    descending RRF score.  Sessions absent from one list are penalised with
    rank = len(that_list) + 1.
    """
    sem_rank = {sid: i + 1 for i, (sid, _) in enumerate(sem_ranked)}
    kw_rank  = {sid: i + 1 for i, (sid, _) in enumerate(kw_ranked)}
    sem_default = len(sem_ranked) + 1
    kw_default  = len(kw_ranked) + 1

    all_ids = {sid for sid, _ in sem_ranked} | {sid for sid, _ in kw_ranked}
    merged = [
        (sid, 1.0 / (k + sem_rank.get(sid, sem_default))
               + 1.0 / (k + kw_rank.get(sid, kw_default)))
        for sid in all_ids
    ]
    merged.sort(key=lambda x: x[1], reverse=True)
    return merged


def _length_penalty(doc_text: str, slope: float = _LN_SLOPE, pivot: float = _LN_PIVOT) -> float:
    """Pivoted length normalization multiplier (BM25-style).

    Returns a value > 1 for documents shorter than *pivot* (mild boost) and
    < 1 for documents longer than *pivot* (mild penalty).  Documents of exactly
    *pivot* characters are returned unchanged (multiplier = 1.0).
    """
    length = max(1, len(doc_text))
    return 1.0 / (1.0 - slope + slope * (length / pivot))


def _rank_matches(query_vec: np.ndarray, cmd_vecs: np.ndarray) -> List[int]:
    """Pick the command indices that best match the query.

    Returns up to :data:`MAX_MATCHED_INDICES` indices, best first, restricted
    to commands within :data:`MATCH_SCORE_MARGIN` of the best-matching command.
    """
    if cmd_vecs.shape[0] == 0:
        return []

    sims = cmd_vecs @ np.asarray(query_vec, dtype=np.float32)
    order = np.argsort(sims)[::-1]
    best = float(sims[order[0]])

    indices: List[int] = []
    for idx in order[:MAX_MATCHED_INDICES]:
        if best - float(sims[idx]) > MATCH_SCORE_MARGIN and indices:
            break
        indices.append(int(idx))
    return indices


def search(
    config: Config,
    query: str,
    *,
    k: Optional[int] = None,
    embedder: Optional[Embedder] = None,
    index: Optional[VectorIndex] = None,
) -> List[SearchResult]:
    """Run a semantic query against the indexed session history.

    Returns sessions ranked by similarity score (descending), each annotated
    with the command indices that best match the query. Returns an empty
    list if the index or database has no data yet.
    """
    embedder = embedder or build_embedder(config)
    index = index or build_index(config)
    index.load()

    if len(index) == 0:
        return []

    qvec = embedder.encode_one(query)
    hits = index.search(qvec, k or config.top_k)
    if not hits:
        return []

    conn = db.connect(config.db_path)
    try:
        sessions = []
        for session_id, score in hits:
            session = db.get_session(conn, session_id)
            if session is None:
                continue
            sessions.append((session, score))
    finally:
        conn.close()

    # Embed every command of every returned session in ONE batch, then slice
    # per session, so highlighting costs a single encode call (not one per
    # session). This keeps query latency dominated by the tiny ANN search.
    all_texts: List[str] = []
    spans: List[tuple] = []  # (start, end) into all_texts for each session
    for session, _ in sessions:
        start = len(all_texts)
        all_texts.extend(c.raw_cmd for c in session.commands)
        spans.append((start, len(all_texts)))

    cmd_vecs = embedder.encode(all_texts) if all_texts else np.empty((0, embedder.dim), np.float32)
    qv = np.asarray(qvec, dtype=np.float32)

    results: List[SearchResult] = []
    for (session, score), (start, end) in zip(sessions, spans):
        matched_indices = _rank_matches(qv, cmd_vecs[start:end])
        adj_score = score * _length_penalty(session.doc_text or "")
        results.append(SearchResult(session=session, score=adj_score, matched_indices=matched_indices))

    results.sort(key=lambda r: r.score, reverse=True)

    if config.hybrid_search:
        # Keyword-score every semantic candidate and merge via RRF, but only
        # when keyword signal is strong enough to be informative.  Pure
        # intent-paraphrase queries produce Jaccard scores near 0 for all
        # sessions; incorporating that noise via RRF degrades semantic
        # rankings.  We therefore gate on the maximum keyword score: if no
        # candidate clears _HYBRID_KW_MIN_SCORE, the pure-semantic order is
        # returned unchanged.
        kw_pairs   = [
            (r.session.id, _keyword_score(query, r.session.doc_text or ""))
            for r in results
        ]
        max_kw = max((sc for _, sc in kw_pairs), default=0.0)
        if max_kw >= _HYBRID_KW_MIN_SCORE:
            sem_ranked = [(r.session.id, r.score) for r in results]
            kw_ranked = sorted(kw_pairs, key=lambda x: x[1], reverse=True)
            merged = _rrf_merge(sem_ranked, kw_ranked)

            id_to_result = {r.session.id: r for r in results}
            results = []
            for sid, rrf_score in merged:
                if sid in id_to_result:
                    r = id_to_result[sid]
                    r.score = rrf_score
                    results.append(r)

    return results
