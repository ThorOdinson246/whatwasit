"""Tests for whatwasit.tui confidence badges, result rendering, and REPL behaviour."""

from __future__ import annotations

from typing import List

import pytest
from textual.widgets import Input, ListView, Static

from whatwasit.models import Command, SearchResult, Session
from whatwasit.config_loader import load_config_file
from whatwasit.themes import THEME_ORDER, cycle_theme_ids
from whatwasit.tui import (
    TextualBuiltinThemeProvider,
    WhatwasitREPL,
    WhatwasitTUI,
    confidence_level,
    low_confidence_message,
    matched_commands_text,
    render_result_label,
)


def _row_text(list_item) -> str:
    return "\n".join(str(w.render()) for w in list_item.query(Static))


def _cmd(raw_cmd: str) -> Command:
    return Command(raw_cmd=raw_cmd, source="zsh")


def _make_results(n: int = 3, *, base_score: float = 0.9) -> List[SearchResult]:
    results: List[SearchResult] = []
    for i in range(n):
        session = Session(
            cwd=f"/tmp/project-{i}",
            start_ts=1_700_000_000 + i,
            commands=[_cmd(f"echo session-{i}"), _cmd(f"git status {i}")],
        )
        results.append(
            SearchResult(session=session, score=base_score - i * 0.1, matched_indices=[1])
        )
    return results


def test_confidence_level_bands() -> None:
    results = _make_results(2, base_score=0.9)
    assert confidence_level(results[0], 1, results) == "strong"

    medium = SearchResult(
        session=results[0].session,
        score=0.42,
        matched_indices=[0],
    )
    assert confidence_level(medium, 1, [medium]) == "medium"

    weak = SearchResult(
        session=results[0].session,
        score=0.30,
        matched_indices=[0],
    )
    assert confidence_level(weak, 1, [weak]) == "weak"


def test_low_confidence_message_below_threshold() -> None:
    results = _make_results(1, base_score=0.35)
    msg = low_confidence_message(results, threshold=0.40)
    assert msg is not None
    assert "No confident matches" in msg


def test_low_confidence_message_above_threshold() -> None:
    results = _make_results(1, base_score=0.55)
    assert low_confidence_message(results, threshold=0.40) is None


def test_render_result_label_shows_primary_command() -> None:
    results = _make_results(1)
    text = render_result_label(results[0], results, 1)
    rendered = str(text)
    assert "git status 0" in rendered
    assert "/tmp/project-0" in rendered
    assert "score=" not in rendered
    assert "[strong]" not in rendered


def test_render_result_label_shows_weak_indicator_on_right() -> None:
    weak = SearchResult(
        session=_make_results(1)[0].session,
        score=0.30,
        matched_indices=[1],
    )
    rendered = str(render_result_label(weak, [weak], 1, line_width=60))
    assert "⚠" in rendered
    assert rendered.index("git status") < rendered.index("⚠")

    strong = _make_results(1)[0]
    rendered_strong = str(render_result_label(strong, [strong], 1, line_width=60))
    assert "⚠" not in rendered_strong


def test_matched_commands_text_returns_highlighted_only() -> None:
    results = _make_results(1)
    text = matched_commands_text(results[0])
    assert text == "git status 0"
    assert "echo session-0" not in text


@pytest.mark.asyncio
async def test_tui_shows_commands_and_banner() -> None:
    results = _make_results(2, base_score=0.35)
    app = WhatwasitTUI(results, "docker build", page_size=5, low_confidence_threshold=0.40)

    async with app.run_test() as pilot:
        list_view = pilot.app.query_one("#results", ListView)
        assert len(list_view.children) == 2
        first_label = _row_text(list_view.children[0])
        assert "git status 0" in first_label
        assert "/tmp/project-0" in first_label

        banner = pilot.app.query_one("#banner", Static)
        assert banner.display is True
        assert "No confident matches" in str(banner.render())


@pytest.mark.asyncio
async def test_tui_navigate_and_load_more() -> None:
    results = _make_results(6)
    app = WhatwasitTUI(results, "docker build", page_size=5)

    async with app.run_test() as pilot:
        await pilot.press("j")
        list_view = pilot.app.query_one("#results", ListView)
        assert list_view.index == 1
        await pilot.press("m")
        list_view = pilot.app.query_one("#results", ListView)
        assert len(list_view.children) == 6


@pytest.mark.asyncio
async def test_tui_copy_on_select(monkeypatch: pytest.MonkeyPatch) -> None:
    results = _make_results(1)
    app = WhatwasitTUI(results, "git status", page_size=5)
    copied: list[str] = []
    monkeypatch.setattr(
        "whatwasit.tui.copy_to_system_clipboard",
        lambda text: copied.append(text) or True,
    )

    async with app.run_test() as pilot:
        await pilot.press("enter")
        assert copied == ["git status 0"]


@pytest.mark.asyncio
async def test_repl_debounced_live_search() -> None:
    queries: list[str] = []

    def fake_search(query: str):
        queries.append(query)
        return _make_results(1)

    app = WhatwasitREPL(fake_search, page_size=5)

    async with app.run_test() as pilot:
        prompt = pilot.app.query_one("#prompt", Input)
        prompt.value = "git"
        pilot.app.on_input_changed(Input.Changed(prompt, prompt.value))
        await pilot.pause(0.5)
        assert queries == ["git"]


@pytest.mark.asyncio
async def test_tui_toggle_expand() -> None:
    results = _make_results(1)
    app = WhatwasitTUI(results, "git status", page_size=5)

    async with app.run_test() as pilot:
        await pilot.press("space")
        assert 0 in pilot.app._expanded_rows
        await pilot.press("space")
        assert 0 not in pilot.app._expanded_rows


@pytest.mark.asyncio
async def test_repl_query_and_slash_commands() -> None:
    queries: list[str] = []

    def fake_search(query: str) -> List[SearchResult]:
        queries.append(query)
        return _make_results(2)

    app = WhatwasitREPL(fake_search, page_size=5)

    async with app.run_test() as pilot:
        prompt = pilot.app.query_one("#prompt", Input)
        prompt.value = "nginx fix"
        await pilot.press("enter")
        assert queries == ["nginx fix"]
        header = str(pilot.app.query_one("#header", Static).render())
        assert "2 of 2" in header
        assert prompt.value == "nginx fix"

        prompt.value = "/more"
        await pilot.press("enter")
        header = str(pilot.app.query_one("#header", Static).render())
        assert "2 of 2" in header

        prompt.value = "/help"
        await pilot.press("enter")
        help_text = str(pilot.app.query_one("#header", Static).render())
        assert "Slash commands" in help_text

        prompt.value = "/settings"
        await pilot.press("enter")
        settings_text = str(pilot.app.query_one("#header", Static).render())
        assert "whatwasit settings" in settings_text
        assert "midnight" in settings_text


def test_change_theme_overrides_textual_default() -> None:
    from textual.app import App

    assert WhatwasitREPL.action_change_theme is not App.action_change_theme
    assert WhatwasitTUI.action_change_theme is not App.action_change_theme


@pytest.mark.asyncio
async def test_nested_theme_palette_includes_textual_builtins() -> None:
    app = WhatwasitREPL(lambda q: [])

    async with app.run_test() as pilot:
        provider = TextualBuiltinThemeProvider(pilot.app.screen)
        discovered = [hit async for hit in provider.discover()]

    names = " ".join(str(h) for h in discovered)
    assert "nord" in names
    assert "dracula" in names
    assert len(discovered) >= 10


def test_cycle_theme_ids_covers_custom_and_textual() -> None:
    ids = cycle_theme_ids(["nord", "dracula", "textual-ansi"])
    assert len(ids) == len(THEME_ORDER) + 2
    assert ids[0] == "whatwasit:midnight"
    assert "textual:nord" in ids
    assert "textual:dracula" in ids
    assert not any("textual-ansi" in i for i in ids)


@pytest.mark.asyncio
async def test_t_key_cycles_in_repl_with_search_focus() -> None:
    app = WhatwasitREPL(lambda q: [])

    async with app.run_test() as pilot:
        assert pilot.app.query_one("#prompt", Input).has_focus
        await pilot.press("t")
        assert pilot.app._theme_name == "default"


@pytest.mark.asyncio
async def test_t_key_cycles_past_custom_into_textual() -> None:
    app = WhatwasitTUI([], "query", theme="midnight")

    async with app.run_test() as pilot:
        for _ in range(len(THEME_ORDER)):
            await pilot.press("t")
        assert pilot.app._theme_name == "default"
        assert load_config_file().get("textual_theme") == "atom-one-dark"
