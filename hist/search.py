"""Semantic query search over indexed shell history sessions.

Ties together the embedder, vector index, and SQLite store: a query string is
embedded, the nearest session vectors are looked up, and each matched
session's commands are individually re-ranked against the query so the
output layer can highlight which specific commands made the session relevant.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from .config import Config
from .embedder import build_embedder
from .index import build_index
from .interfaces import Embedder, VectorIndex
from . import db
from .models import SearchResult

MAX_MATCHED_INDICES = 3
MATCH_SCORE_MARGIN = 0.05


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
        results.append(SearchResult(session=session, score=score, matched_indices=matched_indices))

    results.sort(key=lambda r: r.score, reverse=True)
    return results
