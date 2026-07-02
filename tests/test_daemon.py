"""Integration tests for the warm-query daemon."""

from __future__ import annotations

import threading
import time

import pytest

from whatwasit.config import Config
from whatwasit.daemon import DaemonState, daemon_search, serve
from whatwasit import daemon as daemon_mod
from whatwasit.indexer import index_commands
from tests import synthetic


@pytest.fixture
def indexed_config(tmp_path):
    config = Config(data_dir=tmp_path)
    commands = synthetic.generate_commands(200, seed=3)
    index_commands(config, commands, reset=True)
    return config


def test_daemon_handle_search(indexed_config):
    state = DaemonState(indexed_config)
    response = state.handle(
        {"id": 1, "method": "search", "params": {"query": "docker", "k": 3}}
    )
    assert response["ok"] is True
    assert response["result"]["results"]


def test_daemon_search_round_trip(indexed_config, monkeypatch):
    monkeypatch.setattr(
        "whatwasit.daemon.socket_path",
        lambda cfg=None: indexed_config.data_dir / "test.sock",
    )

    thread = threading.Thread(target=serve, args=(indexed_config,), daemon=True)
    thread.start()

    sock = daemon_mod.socket_path(indexed_config)
    for _ in range(100):
        if sock.exists():
            break
        time.sleep(0.1)
    assert sock.exists()

    results = None
    for _ in range(60):
        results = daemon_search(indexed_config, "nginx", k=3)
        if results is not None:
            break
        time.sleep(0.2)

    assert results is not None
    assert len(results) > 0
    assert results[0].session.commands


def test_daemon_state_reloads_index_on_mtime_change(indexed_config):
    state = DaemonState(indexed_config)
    before_mtime = state._index_mtime
    commands = synthetic.generate_commands(400, seed=99)
    index_commands(indexed_config, commands, reset=True)
    state._reload_index_if_needed()
    assert state._index_mtime != before_mtime
    assert len(state.index) > 0
