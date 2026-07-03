"""Tests for incremental index fingerprinting."""

from __future__ import annotations

from whatwasit import db
from whatwasit.index import UsearchIndex
from whatwasit.indexer import build_index_from_history, index_commands
from tests.test_indexer import FakeEmbedder, _make_commands, _make_config


def test_build_index_skips_when_fingerprint_unchanged(tmp_path, monkeypatch) -> None:
    config = _make_config(tmp_path)
    commands = _make_commands()
    index_commands(
        config,
        commands,
        embedder=FakeEmbedder(),
        index=UsearchIndex(config.index_path, dim=16),
    )

    conn_fp = "deadbeef"
    monkeypatch.setattr(
        "whatwasit.indexer.history_fingerprint",
        lambda: conn_fp,
    )
    monkeypatch.setattr("whatwasit.indexer.load_all", lambda _config: commands)

    conn = db.connect(config.db_path)
    db.set_meta(conn, "history_fingerprint", conn_fp)
    conn.commit()
    conn.close()

    stats = build_index_from_history(config)
    assert stats.skipped is True
    assert stats.n_commands == 0


def test_build_index_rebuilds_when_forced(tmp_path, monkeypatch) -> None:
    config = _make_config(tmp_path)
    commands = _make_commands()
    index_commands(
        config,
        commands,
        embedder=FakeEmbedder(),
        index=UsearchIndex(config.index_path, dim=16),
    )

    monkeypatch.setattr(
        "whatwasit.indexer.history_fingerprint",
        lambda: "same-fingerprint",
    )
    monkeypatch.setattr("whatwasit.indexer.load_all", lambda _config: commands)

    conn = db.connect(config.db_path)
    db.set_meta(conn, "history_fingerprint", "same-fingerprint")
    conn.commit()
    conn.close()

    stats = build_index_from_history(
        config,
        force_rebuild=True,
        embedder=FakeEmbedder(),
        index=UsearchIndex(config.index_path, dim=16),
    )
    assert stats.skipped is False
    assert stats.n_commands == len(commands)
