"""Tests for FTS keyword search and hybrid ranking."""

from __future__ import annotations

import pytest

from whatwasit import db
from whatwasit.config import Config
from whatwasit.index import UsearchIndex
from whatwasit.search import build_fts_match_query, looks_literal_query, search
from tests.test_search import FakeEmbedder, _make_sessions, _seed


def test_build_fts_match_query_quotes_tokens() -> None:
    assert build_fts_match_query("docker compose") == '"docker" "compose"'


def test_looks_literal_query_short_tool_names() -> None:
    assert looks_literal_query("nginx")
    assert looks_literal_query("git status")
    assert not looks_literal_query(
        "how do I reload nginx after changing the reverse proxy config"
    )


def test_db_search_fts_finds_session(tmp_path) -> None:
    config = Config(data_dir=tmp_path, embedding_dim=16)
    conn = db.connect(config.db_path)
    db.initialize(conn)
    session = _make_sessions()[0]
    sid = db.insert_session(conn, session)
    session.id = sid
    conn.commit()

    hits = db.search_fts(conn, '"nginx"', limit=5)
    assert hits
    assert hits[0][0] == sid
    conn.close()


@pytest.fixture
def config(tmp_path) -> Config:
    return Config(data_dir=tmp_path, embedding_dim=16, top_k=5)


def test_literal_query_uses_fts_fast_path(config: Config) -> None:
    embedder = FakeEmbedder()
    _seed(config, embedder)
    query_index = UsearchIndex(config.index_path, 16)

    results = search(config, "nginx", embedder=embedder, index=query_index)

    assert results
    assert results[0].session.cwd == "/srv/nginx-proxy"


def test_intent_query_skips_hybrid_rrf(config: Config) -> None:
    intent = "how do I reload nginx after changing the reverse proxy config"
    assert not looks_literal_query(intent)

    embedder = FakeEmbedder()
    _seed(config, embedder)
    query_index = UsearchIndex(config.index_path, 16)

    semantic_only = Config(
        data_dir=config.data_dir, embedding_dim=16, top_k=5, hybrid_search=False
    )
    hybrid_on = Config(
        data_dir=config.data_dir, embedding_dim=16, top_k=5, hybrid_search=True
    )

    r_sem = search(semantic_only, intent, embedder=embedder, index=query_index)
    r_hyb = search(hybrid_on, intent, embedder=embedder, index=query_index)

    assert [r.session.id for r in r_sem] == [r.session.id for r in r_hyb]
    assert [r.score for r in r_sem] == [r.score for r in r_hyb]
