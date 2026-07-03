"""Semantic query search over indexed shell history sessions.

Ties together the embedder, vector index, FTS keyword leg, and SQLite store:
a query string is embedded (unless a short literal fast-path applies), the
nearest session vectors are looked up, and each matched session's commands are
individually re-ranked against the query so the output layer can highlight
which specific commands made the session relevant.
"""

from __future__ import annotations

import re
from typing import List, Optional, Sequence, Tuple

import numpy as np

from .config import Config
from .embedder import build_embedder, encode_passages, encode_query_one
from .index import build_index
from .interfaces import Embedder, VectorIndex
from . import db
from .models import SearchResult, Session
from .textutil import truncate_for_embed

MAX_MATCHED_INDICES = 3
MATCH_SCORE_MARGIN = 0.05

# Pivoted length normalization (BM25-style).
_LN_SLOPE: float = 0.4
_LN_PIVOT: float = 175.0

_RRF_K = 60
_KW_TOKEN_RE = re.compile(r"[a-z0-9_.-]+")

# Lowered from 0.20: intent queries stay < 0.04; tool-name queries clear 0.08+.
_HYBRID_KW_MIN_SCORE: float = 0.08

_SHORT_QUERY_MAX_CHARS = 40
_SHORT_QUERY_MAX_TOKENS = 4

# Minimum FTS score to accept a keyword-only fast path (after negating bm25).
_FTS_FAST_PATH_MIN_SCORE = 0.5


def _strip_hints(doc_text: str) -> str:
    """Return doc_text without the semantic hint expansion line."""
    return "\n".join(
        line for line in doc_text.split("\n") if not line.startswith("context: ")
    )


def looks_literal_query(query: str) -> bool:
    """Heuristic: short, command-shaped queries benefit from keyword-first search."""
    tokens = _KW_TOKEN_RE.findall(query.lower())
    if not tokens or len(tokens) > _SHORT_QUERY_MAX_TOKENS:
        return False
    if len(query) > _SHORT_QUERY_MAX_CHARS:
        return False
    if any(ch in query for ch in "/._-"):
        return True
    return len(tokens) <= 2


def build_fts_match_query(query: str) -> Optional[str]:
    """Build an FTS5 MATCH string from user input (AND of quoted tokens)."""
    terms = _KW_TOKEN_RE.findall(query.lower())
    if not terms:
        return None
    safe = [t.replace('"', "") for t in terms if t.replace('"', "")]
    if not safe:
        return None
    return " ".join(f'"{term}"' for term in safe)


def _keyword_score(query: str, doc_text: str) -> float:
    """Jaccard token-overlap similarity between query and raw command text."""
    raw = _strip_hints(doc_text)
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
    """Merge two ranked lists via Reciprocal Rank Fusion."""
    sem_rank = {sid: i + 1 for i, (sid, _) in enumerate(sem_ranked)}
    kw_rank = {sid: i + 1 for i, (sid, _) in enumerate(kw_ranked)}
    sem_default = len(sem_ranked) + 1
    kw_default = len(kw_ranked) + 1

    all_ids = {sid for sid, _ in sem_ranked} | {sid for sid, _ in kw_ranked}
    merged = [
        (
            sid,
            1.0 / (k + sem_rank.get(sid, sem_default))
            + 1.0 / (k + kw_rank.get(sid, kw_default)),
        )
        for sid in all_ids
    ]
    merged.sort(key=lambda x: x[1], reverse=True)
    return merged


def _length_penalty(doc_text: str, slope: float = _LN_SLOPE, pivot: float = _LN_PIVOT) -> float:
    length = max(1, len(doc_text))
    return 1.0 / (1.0 - slope + slope * (length / pivot))


def _rank_matches(query_vec: np.ndarray, cmd_vecs: np.ndarray) -> List[int]:
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


def _annotate_results(
    embedder: Embedder,
    query: str,
    sessions: Sequence[Tuple[Session, float]],
) -> List[SearchResult]:
    """Embed commands in one batch and build :class:`SearchResult` objects."""
    all_texts: List[str] = []
    spans: List[tuple[int, int]] = []
    for session, _ in sessions:
        start = len(all_texts)
        all_texts.extend(truncate_for_embed(c.raw_cmd) for c in session.commands)
        spans.append((start, len(all_texts)))

    cmd_vecs = (
        encode_passages(embedder, all_texts)
        if all_texts
        else np.empty((0, embedder.dim), np.float32)
    )
    qv = np.asarray(encode_query_one(embedder, query), dtype=np.float32)

    use_length_penalty = not hasattr(embedder, "encode_query")
    results: List[SearchResult] = []
    for (session, score), (start, end) in zip(sessions, spans):
        matched_indices = _rank_matches(qv, cmd_vecs[start:end])
        adj_score = (
            score * _length_penalty(session.doc_text or "")
            if use_length_penalty
            else score
        )
        results.append(
            SearchResult(
                session=session,
                score=adj_score,
                matched_indices=matched_indices,
            )
        )
    results.sort(key=lambda r: r.score, reverse=True)
    return results


def _fts_hits(
    conn,
    query: str,
    *,
    limit: int,
) -> List[Tuple[Session, float]]:
    match = build_fts_match_query(query)
    if match is None:
        return []
    hits = db.search_fts(conn, match, limit=limit)
    sessions: List[Tuple[Session, float]] = []
    for session_id, score in hits:
        session = db.get_session(conn, session_id)
        if session is not None:
            sessions.append((session, score))
    return sessions


def search(
    config: Config,
    query: str,
    *,
    k: Optional[int] = None,
    embedder: Optional[Embedder] = None,
    index: Optional[VectorIndex] = None,
) -> List[SearchResult]:
    """Run a semantic query against the indexed session history."""
    embedder = embedder or build_embedder(config)
    index = index or build_index(config)
    index.load()

    if len(index) == 0:
        return []

    limit = k or config.top_k
    conn = db.connect(config.db_path)
    try:
        db.initialize(conn)

        if looks_literal_query(query):
            fts_sessions = _fts_hits(conn, query, limit=limit)
            if fts_sessions and fts_sessions[0][1] >= _FTS_FAST_PATH_MIN_SCORE:
                return _annotate_results(embedder, query, fts_sessions)

        qvec = encode_query_one(embedder, query)
        hits = index.search(qvec, limit)
        if not hits:
            return []

        sessions: List[Tuple[Session, float]] = []
        for session_id, score in hits:
            session = db.get_session(conn, session_id)
            if session is not None:
                sessions.append((session, score))

        results = _annotate_results(embedder, query, sessions)

        if not config.hybrid_search or not looks_literal_query(query):
            return results

        kw_pairs = [
            (r.session.id, _keyword_score(query, r.session.doc_text or ""))
            for r in results
        ]
        max_kw = max((sc for _, sc in kw_pairs), default=0.0)

        fts_ranked = [
            (sid, score) for sid, score in db.search_fts(
                conn,
                build_fts_match_query(query) or "",
                limit=max(limit, len(results)),
            )
        ] if build_fts_match_query(query) else []

        use_hybrid = max_kw >= _HYBRID_KW_MIN_SCORE or bool(fts_ranked)
        if not use_hybrid:
            return results

        sem_ranked = [(r.session.id, r.score) for r in results]
        if fts_ranked:
            kw_ranked = fts_ranked
        else:
            kw_ranked = sorted(kw_pairs, key=lambda x: x[1], reverse=True)

        merged = _rrf_merge(sem_ranked, kw_ranked)
        id_to_result = {r.session.id: r for r in results}
        hybrid_results: List[SearchResult] = []
        for sid, rrf_score in merged:
            if sid in id_to_result:
                r = id_to_result[sid]
                r.score = rrf_score
                hybrid_results.append(r)

        # Surface FTS-only sessions that semantic retrieval missed.
        for sid, fts_score in fts_ranked:
            if sid not in id_to_result:
                session = db.get_session(conn, sid)
                if session is not None:
                    extra = _annotate_results(embedder, query, [(session, fts_score)])
                    if extra:
                        extra[0].score = fts_score
                        hybrid_results.append(extra[0])

        hybrid_results.sort(key=lambda r: r.score, reverse=True)
        return hybrid_results[:limit]
    finally:
        conn.close()
