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


def _matched_indices(query_vec: np.ndarray, command_texts: List[str], embedder: Embedder) -> List[int]:
    """Rank a session's commands by similarity to the query vector.

    Returns up to :data:`MAX_MATCHED_INDICES` indices, best first, restricted
    to commands within :data:`MATCH_SCORE_MARGIN` of the best-matching command.
    """
    if not command_texts:
        return []

    cmd_vecs = embedder.encode(command_texts)
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
        results: List[SearchResult] = []
        for session_id, score in hits:
            session = db.get_session(conn, session_id)
            if session is None:
                continue
            command_texts = [c.raw_cmd for c in session.commands]
            matched_indices = _matched_indices(qvec, command_texts, embedder)
            results.append(SearchResult(session=session, score=score, matched_indices=matched_indices))
    finally:
        conn.close()

    results.sort(key=lambda r: r.score, reverse=True)
    return results
