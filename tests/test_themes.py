"""Tests for TUI themes."""

from __future__ import annotations

from whatwasit.themes import DEFAULT_THEME, next_theme, normalize_theme, theme_css


def test_normalize_theme_unknown_falls_back() -> None:
    assert normalize_theme("not-a-theme") == DEFAULT_THEME


def test_next_theme_cycles() -> None:
    first = normalize_theme("midnight")
    second = next_theme(first)
    assert second != first
    assert normalize_theme(second) == second


def test_theme_css_includes_class() -> None:
    css = theme_css("midnight")
    assert "theme-midnight" in css
