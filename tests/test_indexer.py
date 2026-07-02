"""Tests for whatwasit.indexer.

Uses a deterministic, fully offline fake embedder (no model loading, no
network) so these tests stay fast and hermetic.
"""

from __future__ import annotations

import hashlib
from typing import Sequence

import numpy as np
import pytest

from whatwasit import db
from whatwasit.config import Config
from whatwasit.index import UsearchIndex
from whatwasit.indexer import IndexStats, index_commands
from whatwasit.interfaces import Embedder
from whatwasit.models import Command

DIM = 16


class FakeEmbedder(Embedder):
    """Deterministic, offline embedder for tests.

    Hashes each whitespace token into a fixed-size vector and L2-normalizes
    the result, so the same text always maps to the same vector without
    loading any real model.
    """

    def __init__(self, dim: int = DIM) -> None:
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        texts = list(texts)
        if not texts:
            return np.empty((0, self._dim), dtype=np.float32)

        vectors = np.zeros((len(texts), self._dim), dtype=np.float32)
        for i, text in enumerate(texts):
            vec = np.zeros(self._dim, dtype=np.float32)
            for token in text.split():
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                idx = digest[0] % self._dim
                sign = 1.0 if digest[1] % 2 == 0 else -1.0
                vec[idx] += sign
            norm = np.linalg.norm(vec)
            if norm == 0:
                vec[0] = 1.0
                norm = 1.0
            vectors[i] = vec / norm
        return vectors.astype(np.float32)


def _make_commands() -> list[Command]:
    return [
        Command(raw_cmd="git status", ts=1000, source="zsh", cwd="/home/u/proj"),
        Command(raw_cmd="git diff", ts=1010, source="zsh", cwd="/home/u/proj"),
        Command(raw_cmd="git commit -m wip", ts=1020, source="zsh", cwd="/home/u/proj"),
        Command(raw_cmd="ls -la", ts=2000, source="zsh", cwd="/home/u/docs"),
        Command(raw_cmd="cat readme.md", ts=2005, source="zsh", cwd="/home/u/docs"),
        Command(raw_cmd="docker ps", ts=3000, source="zsh", cwd="/home/u/infra"),
    ]


def _make_config(tmp_path) -> Config:
    return Config(data_dir=tmp_path, embedding_dim=DIM)


def test_index_commands_populates_db_and_index(tmp_path):
    config = _make_config(tmp_path)
    commands = _make_commands()
    embedder = FakeEmbedder(dim=DIM)
    index = UsearchIndex(config.index_path, dim=DIM)

    stats = index_commands(config, commands, embedder=embedder, index=index)

    assert isinstance(stats, IndexStats)
    assert stats.n_commands == len(commands)
    assert stats.elapsed_seconds >= 0

    conn = db.connect(config.db_path)
    try:
        assert stats.n_sessions == db.count_sessions(conn)
        assert stats.n_sessions == len(index)
        assert stats.n_sessions >= 2  # at least the cwd-driven groups
    finally:
        conn.close()


def test_index_commands_persists_sessions_with_correct_command_counts(tmp_path):
    config = _make_config(tmp_path)
    commands = _make_commands()
    embedder = FakeEmbedder(dim=DIM)
    index = UsearchIndex(config.index_path, dim=DIM)

    index_commands(config, commands, embedder=embedder, index=index)

    conn = db.connect(config.db_path)
    try:
        sessions = list(db.iter_sessions(conn))
        assert sum(s.command_count for s in sessions) == len(commands)
        for session in sessions:
            assert session.id is not None
    finally:
        conn.close()


def test_index_commands_no_sessions_for_empty_input(tmp_path):
    config = _make_config(tmp_path)
    embedder = FakeEmbedder(dim=DIM)
    index = UsearchIndex(config.index_path, dim=DIM)

    stats = index_commands(config, [], embedder=embedder, index=index)

    assert stats.n_commands == 0
    assert stats.n_sessions == 0
    assert len(index) == 0


def test_index_commands_reset_clears_previous_data(tmp_path):
    config = _make_config(tmp_path)
    commands = _make_commands()

    embedder1 = FakeEmbedder(dim=DIM)
    index1 = UsearchIndex(config.index_path, dim=DIM)
    index_commands(config, commands, embedder=embedder1, index=index1)

    embedder2 = FakeEmbedder(dim=DIM)
    index2 = UsearchIndex(config.index_path, dim=DIM)
    stats = index_commands(
        config, commands[:3], embedder=embedder2, index=index2, reset=True
    )

    conn = db.connect(config.db_path)
    try:
        assert db.count_sessions(conn) == stats.n_sessions
        total_commands = sum(s.command_count for s in db.iter_sessions(conn))
        assert total_commands == 3
    finally:
        conn.close()


def test_index_commands_creates_db_and_index_files(tmp_path):
    config = _make_config(tmp_path)
    commands = _make_commands()[:3]

    stats = index_commands(
        config,
        commands,
        embedder=FakeEmbedder(dim=DIM),
        index=UsearchIndex(config.index_path, dim=DIM),
    )

    assert stats.n_commands == 3
    assert config.db_path.exists()
    assert config.index_path.exists()


def test_index_commands_without_reset_appends_to_existing_data(tmp_path):
    config = _make_config(tmp_path)
    commands = _make_commands()

    first = index_commands(
        config,
        commands[:3],
        embedder=FakeEmbedder(dim=DIM),
        index=UsearchIndex(config.index_path, dim=DIM),
    )

    index2 = UsearchIndex(config.index_path, dim=DIM)
    index2.load()
    second = index_commands(
        config,
        commands[3:],
        embedder=FakeEmbedder(dim=DIM),
        index=index2,
        reset=False,
    )

    conn = db.connect(config.db_path)
    try:
        assert db.count_sessions(conn) == first.n_sessions + second.n_sessions
    finally:
        conn.close()
