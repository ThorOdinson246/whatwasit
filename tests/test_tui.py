"""Tests for whatwasit.tui confidence badges, result rendering, and REPL behaviour."""

from __future__ import annotations

from typing import List

import pytest
from textual.widgets import Input, ListView, Static

from whatwasit.models import Command, SearchResult, Session
from whatwasit.tui import (
    WhatwasitREPL,
    WhatwasitTUI,
    confidence_level,
    low_confidence_message,
    matched_commands_text,
    render_result_label,
)


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


def test_render_result_label_shows_rank_not_score() -> None:
    results = _make_results(1)
    text = render_result_label(1, results[0], results)
    rendered = str(text)
    assert "#1" in rendered
    assert "git status 0" in rendered
    assert "score=" not in rendered
    assert "0.9" not in rendered


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
        first_label = str(list_view.children[0].query_one(Static).render())
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
        await pilot.press("n")
        header_text = str(pilot.app.query_one("#header", Static).render())
        assert "6/6" in header_text


@pytest.mark.asyncio
async def test_tui_copy_on_select() -> None:
    results = _make_results(1)
    app = WhatwasitTUI(results, "git status", page_size=5)
    copied: list[str] = []
    app.copy_to_clipboard = lambda text: copied.append(text)  # type: ignore[method-assign]

    async with app.run_test() as pilot:
        await pilot.press("enter")
        assert copied == ["git status 0"]


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
        assert "nginx fix" in header

        prompt.value = "/more"
        await pilot.press("enter")
        header = str(pilot.app.query_one("#header", Static).render())
        assert "2/2" in header

        prompt.value = "/help"
        await pilot.press("enter")
        help_text = str(pilot.app.query_one("#header", Static).render())
        assert "Slash commands" in help_text
