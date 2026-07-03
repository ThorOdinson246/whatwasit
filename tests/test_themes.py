"""Tests for TUI themes."""

from __future__ import annotations

from whatwasit.themes import (
    DEFAULT_THEME,
    THEME_ORDER,
    combined_stylesheet,
    format_settings_text,
    next_theme,
    normalize_theme,
    theme_css,
)


def test_normalize_theme_unknown_falls_back() -> None:
    assert normalize_theme("not-a-theme") == DEFAULT_THEME


def test_next_theme_cycles_all() -> None:
    seen = {normalize_theme("midnight")}
    current = "midnight"
    for _ in range(len(THEME_ORDER) - 1):
        current = next_theme(current)
        seen.add(current)
    assert seen == set(THEME_ORDER)


def test_theme_css_includes_class() -> None:
    css = theme_css("midnight")
    assert "theme-midnight" in css


def test_combined_stylesheet_includes_every_theme() -> None:
    css = combined_stylesheet()
    for key in THEME_ORDER:
        assert f"theme-{key}" in css


def test_format_settings_lists_all_themes() -> None:
    text = format_settings_text(
        active_theme="midnight",
        page_size=5,
        low_confidence_threshold=0.4,
        output_mode="tui",
        config_path="/tmp/config.toml",
    )
    assert "midnight" in text
    assert "default" in text
    assert "high-contrast" in text
    assert "→" in text
    assert "/tmp/config.toml" in text
