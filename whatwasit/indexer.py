"""End-to-end indexing pipeline: parse -> group -> embed -> store.

Ties together the parser, grouper, embedder, vector index, and SQLite layers
into the single entry point the CLI uses to build (or rebuild) the on-disk
index from shell history.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional

from . import db
from .config import Config
from .embedder import _META_MODEL_NAME, build_embedder, encode_passages
from .index import build_index
from .interfaces import Embedder, VectorIndex
from .models import Command
from .parsers.base import history_fingerprint, load_all
from .sessions import group_commands


@dataclass
class IndexStats:
    """Summary of a completed indexing run."""

    n_commands: int
    n_sessions: int
    elapsed_seconds: float
    skipped: bool = False


def index_commands(
    config: Config,
    commands: List[Command],
    *,
    embedder: Optional[Embedder] = None,
    index: Optional[VectorIndex] = None,
    reset: bool = True,
) -> IndexStats:
    """Group, embed, and persist ``commands`` according to ``config``.

    Groups ``commands`` into sessions, stores them (and their commands) in
    SQLite, embeds each session's document text, and adds the resulting
    vectors to the vector index. Returns stats about the run.
    """
    start = time.perf_counter()

    sessions = group_commands(commands, config)

    config.ensure_data_dir()
    conn = db.connect(config.db_path)
    db.initialize(conn)
    if reset:
        db.reset(conn)

    # NOTE: use explicit `is None` checks rather than `embedder or ...` /
    # `index or ...`: a freshly constructed, empty VectorIndex is falsy
    # (its __len__ is 0), which would otherwise silently discard a valid
    # caller-supplied index.
    if embedder is None:
        embedder = build_embedder(config)
    if index is None:
        index = build_index(config)

    doc_texts: List[str] = []
    session_ids: List[int] = []
    for session in sessions:
        sid = db.insert_session(conn, session)
        doc_texts.append(session.doc_text or session.to_document())
        session_ids.append(sid)

    if sessions:
        vectors = encode_passages(embedder, doc_texts)
        if getattr(embedder, "model_dir", None):
            from .embedder import sync_model_dir_to_db

            sync_model_dir_to_db(conn, embedder.model_dir)
        db.set_meta(conn, _META_MODEL_NAME, config.model_name)
        index.add(session_ids, vectors)
        index.save()

    conn.commit()
    conn.close()

    elapsed = time.perf_counter() - start
    return IndexStats(
        n_commands=len(commands),
        n_sessions=len(sessions),
        elapsed_seconds=elapsed,
    )


def build_index_from_history(
    config: Config,
    *,
    embedder: Optional[Embedder] = None,
    index: Optional[VectorIndex] = None,
    force_rebuild: bool = False,
) -> IndexStats:
    """Load history from all available sources and index when sources changed."""
    config.ensure_data_dir()
    fingerprint = history_fingerprint()

    conn = db.connect(config.db_path)
    db.initialize(conn)
    stored_fp = db.get_meta(conn, "history_fingerprint")
    has_data = db.count_sessions(conn) > 0 and config.index_path.exists()
    conn.close()

    if not force_rebuild and stored_fp == fingerprint and has_data:
        return IndexStats(
            n_commands=0,
            n_sessions=0,
            elapsed_seconds=0.0,
            skipped=True,
        )

    commands = load_all(config)
    stats = index_commands(
        config,
        commands,
        embedder=embedder,
        index=index,
        reset=True,
    )

    conn = db.connect(config.db_path)
    db.set_meta(conn, "history_fingerprint", fingerprint)
    conn.commit()
    conn.close()

    return stats
