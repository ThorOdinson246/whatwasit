"""Textual TUI color themes."""

from __future__ import annotations

from dataclasses import dataclass

# Shared layout rules; theme classes only override colors.
BASE_CSS = """
Screen {
    layout: vertical;
}
#prompt {
    margin: 1 1 0 1;
}
#header {
    padding: 0 1;
    height: auto;
}
#banner {
    height: auto;
    padding: 0 1;
    display: none;
}
#results {
    height: 1fr;
    margin: 1;
}
ListView > ListItem {
    padding: 0 1;
    height: auto;
}
#status {
    height: auto;
    padding: 0 1;
}
"""

THEME_ORDER = ("midnight", "default", "high-contrast")


@dataclass(frozen=True)
class Theme:
    name: str
    label: str
    css: str


THEMES: dict[str, Theme] = {
    "midnight": Theme(
        name="midnight",
        label="Midnight (iCommand)",
        css=BASE_CSS
        + """
Screen.theme-midnight {
    background: #0a0a0a;
}
Screen.theme-midnight #prompt {
    background: #121212;
    color: #f0f0f0;
    border: tall #2e2e2e;
}
Screen.theme-midnight #header,
Screen.theme-midnight #status {
    color: #6e6e6e;
}
Screen.theme-midnight #banner {
    color: #c9a227;
}
Screen.theme-midnight #results {
    background: #0a0a0a;
    border: solid #2e2e2e;
}
Screen.theme-midnight ListView > ListItem {
    background: #0a0a0a;
    color: #d4d4d4;
}
Screen.theme-midnight ListView > ListItem.--highlight {
    background: #1a1a1a;
}
Screen.theme-midnight .row-command {
    color: #ffffff;
    text-style: bold;
}
Screen.theme-midnight .row-meta {
    color: #6e6e6e;
}
Screen.theme-midnight .row-path,
Screen.theme-midnight .row-context {
    color: #5a5a5a;
}
Screen.theme-midnight .row-hint {
    color: #4a4a4a;
    text-style: italic;
}
Screen.theme-midnight .row-warn {
    color: #c9a227;
}
""",
    ),
    "default": Theme(
        name="default",
        label="Textual default",
        css=BASE_CSS
        + """
Screen.theme-default #prompt {
    border: tall $primary-darken-2;
}
Screen.theme-default #results {
    border: solid $primary-darken-2;
}
Screen.theme-default #header,
Screen.theme-default #status {
    color: $text-muted;
}
Screen.theme-default .row-meta,
Screen.theme-default .row-path,
Screen.theme-default .row-context,
Screen.theme-default .row-hint {
    color: $text-muted;
}
Screen.theme-default .row-warn {
    color: $warning;
}
""",
    ),
    "high-contrast": Theme(
        name="high-contrast",
        label="High contrast",
        css=BASE_CSS
        + """
Screen.theme-high-contrast {
    background: #000000;
}
Screen.theme-high-contrast #prompt {
    background: #000000;
    color: #ffffff;
    border: tall #ffffff;
}
Screen.theme-high-contrast #results {
    background: #000000;
    border: solid #ffffff;
}
Screen.theme-high-contrast ListView > ListItem.--highlight {
    background: #333333;
}
Screen.theme-high-contrast .row-command {
    color: #ffffff;
    text-style: bold;
}
Screen.theme-high-contrast .row-meta,
Screen.theme-high-contrast .row-path {
    color: #cccccc;
}
Screen.theme-high-contrast .row-warn {
    color: #ffcc00;
}
""",
    ),
}

DEFAULT_THEME = "midnight"
WEAK_INDICATOR = "⚠"


def normalize_theme(name: str | None) -> str:
    if name and name in THEMES:
        return name
    return DEFAULT_THEME


def next_theme(current: str) -> str:
    current = normalize_theme(current)
    idx = THEME_ORDER.index(current)
    return THEME_ORDER[(idx + 1) % len(THEME_ORDER)]


def theme_css(name: str) -> str:
    return THEMES[normalize_theme(name)].css


SESSION_ROW_CSS = """
SessionRow {
    height: auto;
    width: 100%;
}
SessionRow > Horizontal.headline {
    height: auto;
    width: 100%;
}
SessionRow .row-command {
    width: 1fr;
    text-style: bold;
}
SessionRow .row-warn {
    width: auto;
    padding: 0 1;
}
SessionRow .row-meta {
    width: auto;
    min-width: 12;
    text-align: right;
}
SessionRow .row-path {
    width: 100%;
    padding-left: 2;
}
SessionRow .row-context {
    width: 100%;
    padding-left: 4;
}
SessionRow .row-hint {
    width: 100%;
    padding-left: 2;
    text-style: italic;
}
"""


def combined_stylesheet() -> str:
    """CSS for layout, all theme variants, and result rows.

    Every theme variant is included so cycling with ``t`` only swaps the
    active ``Screen.theme-*`` class.
    """
    variants = ""
    for key in THEME_ORDER:
        block = THEMES[key].css
        if block.startswith(BASE_CSS):
            variants += block[len(BASE_CSS) :]
        else:
            variants += block
    return BASE_CSS + variants + SESSION_ROW_CSS


def format_settings_text(
    *,
    active_theme: str,
    page_size: int,
    low_confidence_threshold: float,
    output_mode: str,
    config_path: str,
) -> str:
    """Human-readable settings panel for the REPL ``/settings`` command."""
    active = normalize_theme(active_theme)
    lines = [
        "whatwasit settings",
        "",
        "Theme",
        f"  Active: {THEMES[active].label} ({active})",
        "  Available:",
    ]
    for key in THEME_ORDER:
        theme = THEMES[key]
        marker = "  → " if key == active else "    "
        lines.append(f"{marker}{key:<14} {theme.label}")
    lines.extend(
        [
            "",
            "  Change: press t to cycle, or /theme <name>",
            "",
            f"Results per page: {page_size}",
            f"Low-confidence threshold: {low_confidence_threshold}",
            f"Output mode (CLI): {output_mode}",
            f"Config file: {config_path}",
            "",
            "Type a search query or /help to return.",
        ]
    )
    return "\n".join(lines)
