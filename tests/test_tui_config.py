"""Tests for config loading, plain output, and TUI smoke checks."""

from __future__ import annotations

import io
from pathlib import Path
from typing import List

import pytest
from textual.widgets import ListView, Static

from hist.config import Config
from hist.config_loader import apply_file_overrides, config_file_path
from hist.models import Command, SearchResult, Session
from hist.output import display_results, render_plain_lines
from hist.tui import HistTUI


def _cmd(raw_cmd: str) -> Command:
    return Command(raw_cmd=raw_cmd, source="zsh")


def _make_results(n: int = 3) -> List[SearchResult]:
    results: List[SearchResult] = []
    for i in range(n):
        session = Session(
            cwd=f"/tmp/project-{i}",
            start_ts=1_700_000_000 + i,
            commands=[_cmd(f"echo session-{i}"), _cmd(f"git status {i}")],
        )
        results.append(SearchResult(session=session, score=0.9 - i * 0.1, matched_indices=[1]))
    return results


# ---------------------------------------------------------------------------
# config precedence
# ---------------------------------------------------------------------------


def test_config_defaults_without_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "empty-config"))
    config = Config.default()
    assert config.output_mode == "tui"
    assert config.tui_page_size == 5
    assert config.low_confidence_threshold == 0.40
    assert config.use_daemon is True


def test_config_file_overrides_defaults(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config_dir = tmp_path / "config" / "hist"
    config_dir.mkdir(parents=True)
    (config_dir / "config.toml").write_text(
        'output_mode = "plain"\n'
        "tui_page_size = 8\n"
        "use_daemon = true\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))

    config = Config.default()
    assert config.output_mode == "plain"
    assert config.tui_page_size == 8
    assert config.use_daemon is True


def test_config_ignores_invalid_output_mode(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config_dir = tmp_path / "config" / "hist"
    config_dir.mkdir(parents=True)
    (config_dir / "config.toml").write_text('output_mode = "fancy"\n', encoding="utf-8")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))

    config = Config.default()
    assert config.output_mode == "tui"


def test_cli_plain_flag_overrides_config_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from hist import cli

    config_dir = tmp_path / "config" / "hist"
    config_dir.mkdir(parents=True)
    (config_dir / "config.toml").write_text('output_mode = "tui"\n', encoding="utf-8")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))

    calls: List[dict] = []

    def fake_display(results, query, config, *, force_plain=False, console=None):
        calls.append({"force_plain": force_plain, "output_mode": config.output_mode})

    def fake_search(config, query, *, k=None, embedder=None, index=None):
        return []

    monkeypatch.setattr(cli, "display_results", fake_display)
    monkeypatch.setattr(cli, "search", fake_search)

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "hist.db").touch()

    def fake_default():
        return Config(data_dir=data_dir, output_mode="tui")

    monkeypatch.setattr(cli.Config, "default", staticmethod(fake_default))

    rc = cli.main(["nginx fix", "--plain"])
    assert rc == 0
    assert calls[0]["force_plain"] is True


# ---------------------------------------------------------------------------
# plain mode rendering
# ---------------------------------------------------------------------------


def test_render_plain_lines_highlights_matched_command() -> None:
    results = _make_results(1)
    buf = io.StringIO()
    render_plain_lines(results, "git status", file=buf)
    output = buf.getvalue()
    assert "git status 0" in output
    assert "> git status 0" in output
    assert "echo session-0" in output


def test_display_results_plain_uses_rich_when_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    from rich.console import Console

    calls: List[dict] = []

    def fake_render(results, query, console=None):
        calls.append({"query": query, "n": len(results)})

    monkeypatch.setattr("hist.output.render_results", fake_render)
    monkeypatch.setattr("hist.output.sys.stdout.isatty", lambda: True)

    config = Config(output_mode="plain")
    display_results(_make_results(1), "query", config)
    assert calls[0]["n"] == 1


def test_display_results_plain_uses_lines_when_not_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: List[dict] = []

    def fake_lines(results, query, *, file=None):
        calls.append({"query": query})

    monkeypatch.setattr("hist.output.render_plain_lines", fake_lines)
    monkeypatch.setattr("hist.output.sys.stdout.isatty", lambda: False)

    config = Config(output_mode="plain")
    display_results(_make_results(1), "query", config)
    assert calls[0]["query"] == "query"


# ---------------------------------------------------------------------------
# TUI smoke (headless, mocked results)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tui_smoke_navigate_and_copy() -> None:
    results = _make_results(6)
    app = HistTUI(results, "docker build", page_size=5)
    copied: list[str] = []
    app.copy_to_clipboard = lambda text: copied.append(text)  # type: ignore[method-assign]

    async with app.run_test() as pilot:
        header = pilot.app.query_one("#header", Static)
        assert "docker build" in str(header.render())
        await pilot.press("j")
        list_view = pilot.app.query_one("#results", ListView)
        assert list_view.index == 1
        assert "git status 1" in str(list_view.children[1].query_one(Static).render())
        await pilot.press("enter")
        assert copied == ["git status 1"]
        await pilot.press("n")
        header_text = str(pilot.app.query_one("#header", Static).render())
        assert "6/6" in header_text


def test_config_file_path_uses_xdg(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    assert config_file_path() == tmp_path / "xdg" / "hist" / "config.toml"
