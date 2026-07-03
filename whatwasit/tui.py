"""Interactive Textual TUI for browsing search results."""

from __future__ import annotations

from typing import Callable, List, Optional, Sequence, Set

from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.command import CommandPalette, DiscoveryHit, Hit, Hits, Provider
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.widgets import Footer, Input, ListItem, ListView, Static

from .brand import CLI_NAME
from .clipboard import copy_to_clipboard as copy_to_system_clipboard
from .config_loader import config_file_path, load_config_file, save_config_value
from .models import SearchResult
from .textutil import truncate_display
from .themes import (
    DEFAULT_THEME,
    THEMES,
    THEME_ORDER,
    WEAK_INDICATOR,
    combined_stylesheet,
    cycle_theme_ids,
    format_settings_text,
    normalize_theme,
)
from .timefmt import format_relative_time

_FOOTER_HINTS = (
    "↑↓ nav  ·  ⏎ copy  ·  space expand  ·  m more  ·  t theme  ·  /settings  ·  q quit"
)
_REPL_DEBOUNCE_SECONDS = 0.35
_LIVE_SEARCH_MIN_CHARS = 2
_COLLAPSED_CONTEXT_CMDS = 1

_BADGE_WEAK_MAX = 0.35
_BADGE_STRONG_MIN = 0.50
_STRONG_MARGIN_MIN = 0.08

_HELP_TEXT = """\
whatwasit REPL — search your shell history by intent

Type in the search box; results update after a short pause.
Matched commands are shown in bold.

Keybindings:
  j/k or ↑/↓   navigate results
  Enter        copy matched command(s) to clipboard
  Space        expand or collapse a session
  m            show more results
  t            cycle color theme (midnight → default → … → github-colorblind)
  ctrl+p       command palette — pick Theme for nested theme list
  q            quit

Slash commands:
  /help        show keybindings
  /settings    show theme and config
  /theme       cycle theme  ·  /theme <name>  pick one
  /more        load more results
  /quit        quit
"""


def confidence_level(
    result: SearchResult,
    rank: int,
    all_results: Sequence[SearchResult],
) -> str:
    """Return qualitative confidence: ``strong``, ``medium``, or ``weak``."""
    score = result.score
    if score < _BADGE_WEAK_MAX:
        return "weak"
    if score < _BADGE_STRONG_MIN:
        return "medium"
    if rank == 1 and len(all_results) > 1:
        margin = score - all_results[1].score
        if margin < _STRONG_MARGIN_MIN:
            return "medium"
    return "strong"


def low_confidence_message(
    results: Sequence[SearchResult],
    threshold: float,
) -> Optional[str]:
    """Banner text when the top result is below *threshold*, else ``None``."""
    if not results:
        return None
    if results[0].score < threshold:
        return (
            "No confident matches for this query — "
            "results below may not be relevant."
        )
    return None


def matched_commands_text(result: SearchResult) -> str:
    """Return matched commands for clipboard copy (falls back to all commands)."""
    matched = set(result.matched_indices)
    lines = [cmd.raw_cmd for i, cmd in enumerate(result.session.commands) if i in matched]
    if lines:
        return "\n".join(lines)
    return "\n".join(cmd.raw_cmd for cmd in result.session.commands)


def _primary_command_index(result: SearchResult) -> int:
    if result.matched_indices:
        return result.matched_indices[0]
    return 0


def _visible_command_indices(
    result: SearchResult,
    *,
    expanded: bool,
) -> tuple[List[int], int]:
    """Return command indices to render and how many remain hidden."""
    commands = result.session.commands
    if expanded or len(commands) <= 2:
        return list(range(len(commands))), 0

    primary = _primary_command_index(result)
    visible: Set[int] = set(result.matched_indices)
    for i in range(max(0, primary - _COLLAPSED_CONTEXT_CMDS), primary + 1):
        visible.add(i)
    ordered = sorted(visible)
    hidden = len(commands) - len(ordered)
    return ordered, hidden


def _meta_label(rel_time: str, *, weak: bool) -> str:
    if weak:
        return f"{WEAK_INDICATOR}  {rel_time}"
    return rel_time


def render_result_label(
    result: SearchResult,
    all_results: Sequence[SearchResult],
    rank: int,
    *,
    expanded: bool = False,
    line_width: int = 76,
) -> Text:
    """Plain-text row preview (used by tests and plain output)."""
    text = Text()
    session = result.session
    cwd = session.cwd or "?"
    rel = format_relative_time(session.start_ts)
    matched = set(result.matched_indices)
    primary = _primary_command_index(result)
    weak = confidence_level(result, rank, all_results) == "weak"

    left = truncate_display(result.session.commands[primary].raw_cmd)
    right = _meta_label(rel, weak=weak)
    pad = max(1, line_width - len(left) - len(right))
    text.append(left, style="bold")
    text.append(" " * pad)
    text.append(right, style="dim")
    text.append("\n")

    visible_indices, hidden_count = _visible_command_indices(result, expanded=expanded)
    if expanded or len(result.session.commands) > 1:
        text.append(f"  {cwd}\n", style="dim")
        for i in visible_indices:
            if i == primary and not expanded:
                continue
            cmd = truncate_display(result.session.commands[i].raw_cmd)
            if i in matched:
                text.append("  › ", style="bold")
                text.append(f"{cmd}\n", style="bold")
            else:
                text.append("    ", style="dim")
                text.append(f"{cmd}\n", style="dim")
        if hidden_count > 0:
            text.append(f"  + {hidden_count} more — space to expand\n", style="dim italic")
    else:
        text.append(f"  {cwd}\n", style="dim")
    return text


class SearchInput(Input):
    """Search box; empty ``t`` cycles theme instead of typing."""

    def on_key(self, event: Key) -> None:
        if event.key == "t" and not self.value:
            event.prevent_default()
            event.stop()
            self.app.action_cycle_theme()


class SessionRow(Vertical):
    """One search result: command + right-aligned meta, path, optional context."""

    def __init__(
        self,
        result: SearchResult,
        all_results: Sequence[SearchResult],
        rank: int,
        *,
        expanded: bool = False,
    ) -> None:
        super().__init__()
        self._result = result
        self._all_results = all_results
        self._rank = rank
        self._expanded = expanded

    def compose(self) -> ComposeResult:
        result = self._result
        session = result.session
        cwd = session.cwd or "?"
        rel = format_relative_time(session.start_ts)
        matched = set(result.matched_indices)
        primary = _primary_command_index(result)
        weak = confidence_level(result, self._rank, self._all_results) == "weak"
        primary_cmd = truncate_display(session.commands[primary].raw_cmd)

        with Horizontal(classes="headline"):
            yield Static(primary_cmd, classes="row-command")
            if weak:
                yield Static(WEAK_INDICATOR, classes="row-warn")
            yield Static(rel, classes="row-meta")

        visible_indices, hidden_count = _visible_command_indices(
            result, expanded=self._expanded
        )
        multi = len(session.commands) > 1

        if multi or self._expanded:
            yield Static(f"  {cwd}", classes="row-path")
            for i in visible_indices:
                if i == primary and not self._expanded:
                    continue
                cmd = truncate_display(session.commands[i].raw_cmd)
                if i in matched:
                    yield Static(f"  › {cmd}", classes="row-command")
                else:
                    yield Static(f"    {cmd}", classes="row-context")
            if hidden_count > 0:
                yield Static(
                    f"  + {hidden_count} more — space to expand",
                    classes="row-hint",
                )
        else:
            yield Static(f"  {cwd}", classes="row-path")


class WhatwasitThemeProvider(Provider):
    """Theme list for the nested palette opened from Ctrl+P → Theme."""

    async def discover(self) -> Hits:
        app = self.app
        if not hasattr(app, "action_set_theme"):
            return
        for key in THEME_ORDER:
            theme = THEMES[key]
            yield DiscoveryHit(
                theme.label,
                lambda k=key: app.action_set_theme(k),
            )

    async def search(self, query: str) -> Hits:
        app = self.app
        if not hasattr(app, "action_set_theme"):
            return
        matcher = self.matcher(query)
        for key in THEME_ORDER:
            theme = THEMES[key]
            if (match := matcher.match(theme.label)) > 0:
                yield Hit(
                    match,
                    matcher.highlight(theme.label),
                    lambda k=key: app.action_set_theme(k),
                )


class TextualBuiltinThemeProvider(Provider):
    """Textual built-in themes (Nord, Dracula, …) in the nested Theme palette."""

    async def discover(self) -> Hits:
        app = self.app
        if not hasattr(app, "action_apply_textual_theme"):
            return
        for name in sorted(app.available_themes):
            if name == "textual-ansi":
                continue
            yield DiscoveryHit(
                name,
                lambda n=name: app.action_apply_textual_theme(n),
            )

    async def search(self, query: str) -> Hits:
        app = self.app
        if not hasattr(app, "action_apply_textual_theme"):
            return
        matcher = self.matcher(query)
        for name in sorted(app.available_themes):
            if name == "textual-ansi":
                continue
            if (match := matcher.match(name)) > 0:
                yield Hit(
                    match,
                    matcher.highlight(name),
                    lambda n=name: app.action_apply_textual_theme(n),
                )


class _ThemedAppMixin:
    """Apply and cycle Textual color themes."""

    _theme_name: str
    _page_size: int = 5
    _low_confidence_threshold: float = 0.40
    _output_mode: str = "tui"
    _config_path: str = ""

    def _apply_theme(self, name: str) -> None:
        self._theme_name = normalize_theme(name)
        screen = self.screen
        for theme in THEMES:
            screen.remove_class(f"theme-{theme}")
        screen.add_class(f"theme-{self._theme_name}")

    def action_set_theme(self, name: str) -> None:
        """Set a whatwasit custom theme by key."""
        key = name.lower().strip()
        if key not in THEMES:
            available = ", ".join(THEME_ORDER)
            self.notify(
                f"Unknown theme {name!r} — try: {available}",
                severity="warning",
                timeout=4,
            )
            return
        self._theme_name = key
        save_config_value("tui_theme", self._theme_name)
        save_config_value("textual_theme", "")
        self._apply_theme(self._theme_name)
        label = THEMES[self._theme_name].label
        self.notify(f"Theme: {label}", timeout=2)

    def action_apply_textual_theme(self, name: str) -> None:
        """Apply a Textual built-in theme (uses the default whatwasit CSS layer)."""
        if name not in self.available_themes:
            self.notify(f"Unknown theme {name!r}", severity="warning", timeout=3)
            return
        self.theme = name
        self._theme_name = "default"
        self._apply_theme("default")
        save_config_value("tui_theme", "default")
        save_config_value("textual_theme", name)
        self.notify(f"Theme: {name}", timeout=2)

    def _restore_textual_theme(self) -> None:
        """Re-apply saved Textual theme when using the default whatwasit layer."""
        if self._theme_name != "default":
            return
        data = load_config_file()
        name = data.get("textual_theme")
        if isinstance(name, str) and name in self.available_themes:
            self.theme = name

    def _active_theme_id(self) -> str:
        if self._theme_name != "default":
            return f"whatwasit:{self._theme_name}"
        data = load_config_file()
        name = data.get("textual_theme")
        if isinstance(name, str) and name and name in self.available_themes:
            return f"textual:{name}"
        return "whatwasit:default"

    def action_cycle_theme(self) -> None:
        """Cycle ``t`` through custom and Textual built-in themes."""
        ids = cycle_theme_ids(self.available_themes.keys())
        current = self._active_theme_id()
        try:
            idx = ids.index(current)
        except ValueError:
            idx = -1
        kind, name = ids[(idx + 1) % len(ids)].split(":", 1)
        if kind == "whatwasit":
            self.action_set_theme(name)
        else:
            self.action_apply_textual_theme(name)

    def action_change_theme(self) -> None:
        """Open nested palette (Ctrl+P → Theme) with custom + Textual themes."""
        self.push_screen(
            CommandPalette(
                providers=[WhatwasitThemeProvider, TextualBuiltinThemeProvider],
                placeholder="Search for themes…",
            )
        )

    def action_show_settings(self) -> None:
        self.query_one("#header", Static).update(
            format_settings_text(
                active_theme=self._theme_name,
                page_size=self._page_size,
                low_confidence_threshold=self._low_confidence_threshold,
                output_mode=self._output_mode,
                config_path=self._config_path or str(config_file_path()),
            )
        )
        self.query_one("#banner", Static).display = False


class _ResultPanelMixin(_ThemedAppMixin):
    """Shared result-list behaviour for one-shot TUI and REPL."""

    _all_results: List[SearchResult]
    _query: str
    _page_size: int
    _visible_count: int
    _low_confidence_threshold: float
    _expanded_rows: Set[int]

    def _header_text(self) -> str:
        if not self._all_results:
            if self._query:
                return f'No results for: "{self._query}"'
            return "Type to search your shell history"
        shown = min(self._visible_count, len(self._all_results))
        total = len(self._all_results)
        return f"{shown} of {total} sessions"

    def _banner_text(self) -> str:
        msg = low_confidence_message(self._all_results, self._low_confidence_threshold)
        return msg or ""

    def _refresh_list(self) -> None:
        list_view = self.query_one("#results", ListView)
        list_view.clear()
        visible = self._all_results[: self._visible_count]
        for rank, result in enumerate(visible, start=1):
            row_index = rank - 1
            list_view.append(
                ListItem(
                    SessionRow(
                        result,
                        self._all_results,
                        rank,
                        expanded=row_index in self._expanded_rows,
                    )
                )
            )
        if visible and list_view.index is None:
            list_view.index = 0

    def _selected_row_index(self) -> Optional[int]:
        list_view = self.query_one("#results", ListView)
        index = list_view.index
        if index is None or index < 0:
            return None
        return index

    def _selected_result(self) -> Optional[SearchResult]:
        index = self._selected_row_index()
        if index is None:
            return None
        visible = self._all_results[: self._visible_count]
        if index >= len(visible):
            return None
        return visible[index]

    def _update_banner(self) -> None:
        banner = self.query_one("#banner", Static)
        text = self._banner_text()
        if text:
            banner.update(Text(text, style="bold yellow"))
            banner.display = True
        else:
            banner.update("")
            banner.display = False

    def _set_status(self, message: str) -> None:
        status = self.query_one("#status", Static)
        status.update(message or _FOOTER_HINTS)

    def _refresh_results_ui(self) -> None:
        header = self.query_one("#header", Static)
        header.update(self._header_text())
        self._update_banner()
        self._refresh_list()
        self._set_status(_FOOTER_HINTS)

    def _copy_text(self, text: str) -> None:
        if copy_to_system_clipboard(text):
            self.notify("Copied to clipboard", title="whatwasit", timeout=2)
            return
        try:
            self.copy_to_clipboard(text)
            self.notify("Copied to clipboard", title="whatwasit", timeout=2)
        except Exception:
            self.notify(
                "Copy failed — install wl-copy or xclip",
                title="whatwasit",
                severity="error",
                timeout=4,
            )

    def _copy_selected(self) -> None:
        result = self._selected_result()
        if result is None:
            return
        self._copy_text(matched_commands_text(result))

    def action_toggle_expand(self) -> None:
        index = self._selected_row_index()
        if index is None:
            return
        if index in self._expanded_rows:
            self._expanded_rows.remove(index)
        else:
            self._expanded_rows.add(index)
        self._refresh_list()
        list_view = self.query_one("#results", ListView)
        list_view.index = index

    def action_cursor_down(self) -> None:
        list_view = self.query_one("#results", ListView)
        if list_view.index is not None and list_view.index < len(list_view.children) - 1:
            list_view.index += 1

    def action_cursor_up(self) -> None:
        list_view = self.query_one("#results", ListView)
        if list_view.index is not None and list_view.index > 0:
            list_view.index -= 1

    def action_load_more(self) -> None:
        if self._visible_count >= len(self._all_results):
            self.notify("No more results", timeout=2)
            return
        self._visible_count = min(
            self._visible_count + self._page_size,
            len(self._all_results),
        )
        self._refresh_results_ui()

    def action_copy(self) -> None:
        self._copy_selected()

    def action_show_help(self) -> None:
        self.query_one("#header", Static).update(_HELP_TEXT)
        self.query_one("#banner", Static).display = False

    def action_focus_results(self) -> None:
        self.query_one("#results", ListView).focus()

    def action_focus_prompt(self) -> None:
        try:
            self.query_one("#prompt", Input).focus()
        except Exception:
            pass


def _app_css() -> str:
    return combined_stylesheet()


class WhatwasitTUI(_ResultPanelMixin, App[None]):
    """Browse pre-fetched search results (one-shot ``whatwasit "query"``)."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("escape", "quit", "Quit", show=False),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("down", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("up", "cursor_up", "Up"),
        Binding("m", "load_more", "More"),
        Binding("enter", "copy", "Copy"),
        Binding("space", "toggle_expand", "Expand", show=False),
        Binding("t", "cycle_theme", "Theme"),
        Binding("tab", "focus_results", "Results", show=False),
    ]

    CSS = _app_css()

    def __init__(
        self,
        results: List[SearchResult],
        query: str,
        *,
        page_size: int = 5,
        low_confidence_threshold: float = 0.40,
        theme: str = DEFAULT_THEME,
        output_mode: str = "tui",
        config_path: str = "",
    ) -> None:
        super().__init__()
        self._all_results = results
        self._query = query
        self._page_size = max(1, page_size)
        self._visible_count = min(self._page_size, len(results))
        self._low_confidence_threshold = low_confidence_threshold
        self._output_mode = output_mode
        self._config_path = config_path or str(config_file_path())
        self._expanded_rows: Set[int] = set()
        self._theme_name = normalize_theme(theme)

    def compose(self) -> ComposeResult:
        yield Static(self._query, id="header")
        yield Static("", id="banner")
        yield ListView(id="results")
        yield Static(_FOOTER_HINTS, id="status")
        yield Footer()

    def on_mount(self) -> None:
        self._apply_theme(self._theme_name)
        self._restore_textual_theme()
        self._refresh_results_ui()

    def _refresh_results_ui(self) -> None:
        self.query_one("#header", Static).update(self._query)
        self._update_banner()
        self._refresh_list()
        self._set_status(_FOOTER_HINTS)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self._copy_selected()


class WhatwasitREPL(_ResultPanelMixin, App[None]):
    """Persistent interactive REPL launched by bare ``whatwasit``."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("escape", "quit", "Quit", show=False),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("down", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("up", "cursor_up", "Up"),
        Binding("m", "load_more", "More"),
        Binding("enter", "copy", "Copy"),
        Binding("space", "toggle_expand", "Expand", show=False),
        Binding("t", "cycle_theme", "Theme"),
        Binding("tab", "focus_results", "Results", show=False),
        Binding("shift+tab", "focus_prompt", "Search", show=False),
        Binding("ctrl+c", "quit", "Quit", show=False),
    ]

    CSS = _app_css()

    def __init__(
        self,
        search_fn: Callable[[str], List[SearchResult]],
        *,
        page_size: int = 5,
        low_confidence_threshold: float = 0.40,
        theme: str = DEFAULT_THEME,
        output_mode: str = "tui",
        config_path: str = "",
    ) -> None:
        super().__init__()
        self._search_fn = search_fn
        self._all_results: List[SearchResult] = []
        self._query = ""
        self._page_size = max(1, page_size)
        self._visible_count = 0
        self._low_confidence_threshold = low_confidence_threshold
        self._output_mode = output_mode
        self._config_path = config_path or str(config_file_path())
        self._expanded_rows: Set[int] = set()
        self._debounce_timer = None
        self._pending_live_query = ""
        self._search_token = 0
        self._theme_name = normalize_theme(theme)

    def compose(self) -> ComposeResult:
        yield SearchInput(placeholder="Search shell history…", id="prompt")
        yield Static("Type to search your shell history", id="header")
        yield Static("", id="banner")
        yield ListView(id="results")
        yield Static(_FOOTER_HINTS, id="status")
        yield Footer()

    def on_mount(self) -> None:
        self._apply_theme(self._theme_name)
        self._restore_textual_theme()
        self.query_one("#prompt", SearchInput).focus()

    def _cancel_debounce(self) -> None:
        if self._debounce_timer is not None:
            self._debounce_timer.stop()
            self._debounce_timer = None

    def _debounced_search(self) -> None:
        self._debounce_timer = None
        query = self._pending_live_query.strip()
        if query and not query.startswith("/"):
            self._schedule_search(query)

    def on_input_changed(self, event: Input.Changed) -> None:
        value = event.value
        self._pending_live_query = value
        self._cancel_debounce()
        stripped = value.strip()
        if not stripped or stripped.startswith("/"):
            return
        self._debounce_timer = self.set_timer(
            _REPL_DEBOUNCE_SECONDS,
            self._debounced_search,
        )

    def _schedule_search(self, query: str) -> None:
        if len(query.strip()) < _LIVE_SEARCH_MIN_CHARS:
            return
        self._query = query
        self._expanded_rows.clear()
        self._search_token += 1
        token = self._search_token
        self._set_status("searching…")
        self._search_worker(query, token)

    @work(thread=True, exclusive=True, group="search")
    def _search_worker(self, query: str, token: int) -> None:
        results = self._search_fn(query)
        self.call_from_thread(self._apply_search_results, query, token, results)

    def _apply_search_results(
        self,
        query: str,
        token: int,
        results: List[SearchResult],
    ) -> None:
        if token != self._search_token:
            return
        self._query = query
        self._all_results = results
        self._visible_count = min(self._page_size, len(results))
        self._refresh_results_ui()

    def _handle_slash(self, raw: str) -> None:
        cmd = raw.strip().lower()
        if cmd in ("/quit", "/q", "/exit"):
            self.exit()
            return
        if cmd == "/help":
            self.action_show_help()
            return
        if cmd in ("/more", "/m"):
            self.action_load_more()
            return
        if cmd in ("/settings", "/config"):
            self.action_show_settings()
            return
        if cmd.startswith("/theme"):
            parts = raw.strip().split(maxsplit=1)
            if len(parts) == 1 or not parts[1].strip():
                self.action_cycle_theme()
            else:
                self.action_set_theme(parts[1].strip())
            return
        self.notify(f"Unknown command: {raw!r} — try /help", severity="warning", timeout=3)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._cancel_debounce()
        value = event.value.strip()
        if not value:
            return
        if value.startswith("/"):
            event.input.value = ""
            self._handle_slash(value)
            return
        self._schedule_search(value)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self._copy_selected()


def run_tui(
    results: List[SearchResult],
    query: str,
    *,
    page_size: int = 5,
    low_confidence_threshold: float = 0.40,
    theme: str = DEFAULT_THEME,
    output_mode: str = "tui",
    config_path: str = "",
) -> None:
    """Launch the one-shot interactive TUI (blocking)."""
    WhatwasitTUI(
        results,
        query,
        page_size=page_size,
        low_confidence_threshold=low_confidence_threshold,
        theme=theme,
        output_mode=output_mode,
        config_path=config_path,
    ).run()


def run_repl(
    search_fn: Callable[[str], List[SearchResult]],
    *,
    page_size: int = 5,
    low_confidence_threshold: float = 0.40,
    theme: str = DEFAULT_THEME,
    output_mode: str = "tui",
    config_path: str = "",
) -> None:
    """Launch the persistent REPL (blocking)."""
    WhatwasitREPL(
        search_fn,
        page_size=page_size,
        low_confidence_threshold=low_confidence_threshold,
        theme=theme,
        output_mode=output_mode,
        config_path=config_path,
    ).run()
