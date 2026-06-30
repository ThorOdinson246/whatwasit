"""Tests for hist.search.

Uses a deterministic bag-of-keywords ``FakeEmbedder`` so these tests run
fully offline with no model downloads, independent of the real
fastembed-backed embedder.
"""

from __future__ import annotations

import re
from typing import Sequence

import numpy as np
import pytest

from hist import db
from hist.config import Config
from hist.index import UsearchIndex
from hist.interfaces import Embedder
from hist.models import Command, Session
from hist.search import search

DIM = 16

VOCAB = [
    "nginx",
    "reverse",
    "proxy",
    "reload",
    "ssl",
    "certbot",
    "config",
    "systemctl",
    "docker",
    "compose",
    "container",
    "build",
    "image",
    "postgres",
    "psql",
    "backup",
]
assert len(VOCAB) == DIM

_TOKEN_RE = re.compile(r"[a-z0-9_]+")


class FakeEmbedder(Embedder):
    """Deterministic bag-of-keywords embedder over a small fixed vocabulary.

    Each dimension corresponds to a vocab word; a text's vector has 1.0 in
    the dimensions for vocab words it contains (as whole tokens), then is
    L2-normalized. No model, no network, no randomness.
    """

    @property
    def dim(self) -> int:
        return DIM

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        texts = list(texts)
        vecs = np.zeros((len(texts), DIM), dtype=np.float32)
        for i, text in enumerate(texts):
            tokens = set(_TOKEN_RE.findall(text.lower()))
            for j, word in enumerate(VOCAB):
                if word in tokens:
                    vecs[i, j] = 1.0
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return (vecs / norms).astype(np.float32)


def _cmd(raw_cmd: str) -> Command:
    return Command(raw_cmd=raw_cmd, source="zsh")


def _make_sessions() -> list[Session]:
    nginx_session = Session(
        cwd="/srv/nginx-proxy",
        start_ts=1000,
        end_ts=1100,
        commands=[
            _cmd("vim /etc/nginx/nginx.conf"),
            _cmd("systemctl reload nginx"),
            _cmd("nginx -t"),
            _cmd("certbot renew"),
        ],
    )
    docker_session = Session(
        cwd="/srv/app",
        start_ts=2000,
        end_ts=2100,
        commands=[
            _cmd("docker build -t myapp ."),
            _cmd("docker compose up -d"),
            _cmd("docker run myapp"),
        ],
    )
    postgres_session = Session(
        cwd="/srv/db",
        start_ts=3000,
        end_ts=3100,
        commands=[
            _cmd("pg_dump mydb > backup.sql"),
            _cmd("psql -U postgres -c select 1"),
            _cmd("systemctl restart postgres"),
        ],
    )
    return [nginx_session, docker_session, postgres_session]


def _seed(config: Config, embedder: FakeEmbedder) -> UsearchIndex:
    """Insert sessions into the DB and build+save a matching vector index."""
    conn = db.connect(config.db_path)
    db.initialize(conn)

    sessions = _make_sessions()
    for session in sessions:
        db.insert_session(conn, session)
    conn.commit()
    conn.close()

    build_index = UsearchIndex(config.index_path, DIM)
    for session in sessions:
        vec = embedder.encode_one(session.to_document())
        build_index.add([session.id], vec.reshape(1, -1))
    build_index.save()

    return build_index


@pytest.fixture
def config(tmp_path) -> Config:
    return Config(data_dir=tmp_path, embedding_dim=DIM, top_k=5)


def test_nginx_session_ranks_first_with_plausible_match(config: Config) -> None:
    embedder = FakeEmbedder()
    _seed(config, embedder)

    query_index = UsearchIndex(config.index_path, DIM)

    results = search(config, "nginx reverse proxy reload", embedder=FakeEmbedder(), index=query_index)

    assert len(results) == 3
    top = results[0]
    assert top.session.cwd == "/srv/nginx-proxy"

    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)

    assert top.matched_indices
    assert all(0 <= idx < len(top.session.commands) for idx in top.matched_indices)
    matched_cmds = [top.session.commands[idx].raw_cmd for idx in top.matched_indices]
    assert any("nginx" in cmd for cmd in matched_cmds)


def test_results_respect_k(config: Config) -> None:
    embedder = FakeEmbedder()
    _seed(config, embedder)

    query_index = UsearchIndex(config.index_path, DIM)

    results = search(config, "docker container build", k=1, embedder=FakeEmbedder(), index=query_index)

    assert len(results) == 1
    assert results[0].session.cwd == "/srv/app"


def test_empty_index_returns_empty_list(config: Config) -> None:
    conn = db.connect(config.db_path)
    db.initialize(conn)
    conn.close()

    empty_index = UsearchIndex(config.index_path, DIM)

    results = search(config, "anything at all", embedder=FakeEmbedder(), index=empty_index)

    assert results == []


def test_missing_index_file_returns_empty_list(config: Config) -> None:
    missing_index = UsearchIndex(config.index_path, DIM)

    results = search(config, "anything at all", embedder=FakeEmbedder(), index=missing_index)

    assert results == []
