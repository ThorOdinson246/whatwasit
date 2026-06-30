"""Tests for hist.cli and hist.output.

CLI routing tests monkeypatch ``hist.cli.search`` and
``hist.cli.build_index_from_history`` with fakes so no model, network, or
on-disk database is needed. Output tests render a hand-built ``SearchResult``
through a recording ``rich.console.Console``.
"""

from __future__ import annotations

from typing import List, Optional

import pytest
from rich.console import Console

from hist import cli
from hist.indexer import IndexStats
from hist.models import Command, SearchResult, Session
from hist.output import format_timestamp, render_results


def _cmd(raw_cmd: str) -> Command:
    return Command(raw_cmd=raw_cmd, source="zsh")


def _make_result() -> SearchResult:
    session = Session(
        cwd="/srv/nginx-proxy",
        start_ts=1_700_000_000,
        end_ts=1_700_000_100,
        commands=[
            _cmd("vim /etc/nginx/nginx.conf"),
            _cmd("systemctl reload nginx"),
            _cmd("nginx -t"),
        ],
    )
    return SearchResult(session=session, score=0.8765, matched_indices=[1])


# ---------------------------------------------------------------------------
# hist.output.format_timestamp
# ---------------------------------------------------------------------------


def test_format_timestamp_none_returns_unknown() -> None:
    assert format_timestamp(None) == "unknown"


def test_format_timestamp_formats_epoch() -> None:
    rendered = format_timestamp(1_700_000_000)
    assert isinstance(rendered, str)
    assert rendered != "unknown"
    # Sanity: should look like a date, e.g. starts with a 4-digit year.
    assert rendered[:1].isdigit()


# ---------------------------------------------------------------------------
# hist.output.render_results
# ---------------------------------------------------------------------------


def test_render_results_highlights_matched_command_and_shows_cwd_and_score() -> None:
    console = Console(record=True, width=120)
    result = _make_result()

    render_results([result], "fix nginx", console=console)

    output = console.export_text()
    assert "systemctl reload nginx" in output  # matched command shown
    assert "/srv/nginx-proxy" in output  # cwd shown
    assert "0.88" in output or "0.87" in output  # score shown (rounded)


def test_render_results_empty_list_does_not_raise() -> None:
    console = Console(record=True, width=120)

    render_results([], "anything", console=console)

    output = console.export_text()
    assert "anything" in output
    assert "No results" in output or "no results" in output.lower()


def test_render_results_defaults_console_when_omitted() -> None:
    # Should not raise even without an injected console.
    render_results([], "no console provided")


# ---------------------------------------------------------------------------
# hist.cli.main routing
# ---------------------------------------------------------------------------


def test_main_no_args_prints_help_and_returns_zero(capsys: pytest.CaptureFixture) -> None:
    rc = cli.main([])

    assert rc == 0
    captured = capsys.readouterr()
    assert "usage" in captured.out.lower()


def test_main_help_flag_prints_help_and_returns_zero(capsys: pytest.CaptureFixture) -> None:
    rc = cli.main(["--help"])

    assert rc == 0
    captured = capsys.readouterr()
    assert "usage" in captured.out.lower()


def test_main_index_calls_build_index_from_history(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: List[dict] = []

    def fake_build_index_from_history(config, **kwargs):
        calls.append({"config": config, "kwargs": kwargs})
        return IndexStats(n_commands=42, n_sessions=7, elapsed_seconds=0.5)

    monkeypatch.setattr(cli, "build_index_from_history", fake_build_index_from_history)

    rc = cli.main(["index"])

    assert rc == 0
    assert len(calls) == 1


def test_main_index_with_window_overrides_config(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_configs = []

    def fake_build_index_from_history(config, **kwargs):
        captured_configs.append(config)
        return IndexStats(n_commands=1, n_sessions=1, elapsed_seconds=0.01)

    monkeypatch.setattr(cli, "build_index_from_history", fake_build_index_from_history)

    rc = cli.main(["index", "--window", "120"])

    assert rc == 0
    assert captured_configs[0].session_window_seconds == 120


def test_main_query_joins_args_and_calls_search(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    calls: List[dict] = []

    def fake_search(config, query, *, k=None, embedder=None, index=None):
        calls.append({"config": config, "query": query, "k": k})
        return []

    monkeypatch.setattr(cli, "search", fake_search)

    # Make the "index exists" check pass without touching the real config.
    def fake_default():
        from hist.config import Config

        config = Config(data_dir=tmp_path)
        config.ensure_data_dir()
        config.db_path.touch()
        return config

    monkeypatch.setattr(cli.Config, "default", staticmethod(fake_default))

    rc = cli.main(["how", "did", "I", "fix", "nginx"])

    assert rc == 0
    assert len(calls) == 1
    assert calls[0]["query"] == "how did I fix nginx"


def test_main_query_supports_top_k_flag(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    calls: List[dict] = []

    def fake_search(config, query, *, k=None, embedder=None, index=None):
        calls.append({"query": query, "k": k})
        return []

    monkeypatch.setattr(cli, "search", fake_search)

    def fake_default():
        from hist.config import Config

        config = Config(data_dir=tmp_path)
        config.ensure_data_dir()
        config.db_path.touch()
        return config

    monkeypatch.setattr(cli.Config, "default", staticmethod(fake_default))

    rc = cli.main(["docker", "build", "-k", "3"])

    assert rc == 0
    assert calls[0]["query"] == "docker build"
    assert calls[0]["k"] == 3


def test_main_query_without_index_prints_hint(monkeypatch: pytest.MonkeyPatch, tmp_path, capsys) -> None:
    def fake_default():
        from hist.config import Config

        return Config(data_dir=tmp_path / "does-not-exist")

    monkeypatch.setattr(cli.Config, "default", staticmethod(fake_default))

    rc = cli.main(["some", "query"])

    assert rc != 0
    captured = capsys.readouterr()
    assert "hist index" in captured.out
