"""Interactive Textual TUI for browsing search results."""

from __future__ import annotations

from typing import Callable, List, Optional, Sequence

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Input, ListItem, ListView, Static

from .brand import CLI_NAME
from .models import SearchResult
from .output import format_timestamp

# Confidence bands from docs/ACCURACY_RESEARCH.md (C2 per-result badges).
_BADGE_STRONG_MIN = 0.50
_BADGE_WEAK_MAX = 0.35
_STRONG_MARGIN_MIN = 0.08

_CONFIDENCE_STYLES = {
    "strong": ("strong", "bold green"),
    "medium": ("medium", "yellow"),
    "weak": ("weak", "dim red"),
}

_HELP_TEXT = """\
whatwasit REPL — search your shell history by intent

Type a natural-language query and press Enter.
Results update in place; matched commands are highlighted.

Keybindings:
  j/k or ↑/↓   navigate results
  Enter        copy matched command(s) to clipboard
  n            show more results
  q            quit

Slash commands:
  /help        show this help
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


def render_result_label(
    rank: int,
    result: SearchResult,
    all_results: Sequence[SearchResult],
) -> Text:
    """Build list item text: commands primary, metadata dim secondary."""
    level = confidence_level(result, rank, all_results)
    label, style = _CONFIDENCE_STYLES[level]

    text = Text()
    text.append(f"#{rank}  ", style="bold")
    text.append(f"[{label}] ", style=style)
    text.append("\n")

    matched = set(result.matched_indices)
    for i, command in enumerate(result.session.commands):
        if i in matched:
            text.append("  > ", style="bold green")
            text.append(f"{command.raw_cmd}\n", style="bold green")
        else:
            text.append("    ", style="dim")
            text.append(f"{command.raw_cmd}\n", style="dim")

    session = result.session
    cwd = session.cwd or "?"
    ts = format_timestamp(session.start_ts)
    text.append(f"  {ts}  {cwd}", style="dim italic")
    return text


class _ResultPanelMixin:
    """Shared result-list behaviour for one-shot TUI and REPL."""

    _all_results: List[SearchResult]
    _query: str
    _page_size: int
    _visible_count: int
    _low_confidence_threshold: float

    def _header_text(self) -> str:
        if not self._all_results:
            return f'No results for: "{self._query}"'
        shown = min(self._visible_count, len(self._all_results))
        total = len(self._all_results)
        return f'Results for: "{self._query}" ({shown}/{total})'

    def _banner_text(self) -> str:
        msg = low_confidence_message(self._all_results, self._low_confidence_threshold)
        return msg or ""

    def _refresh_list(self) -> None:
        list_view = self.query_one("#results", ListView)
        list_view.clear()
        visible = self._all_results[: self._visible_count]
        for rank, result in enumerate(visible, start=1):
            list_view.append(
                ListItem(Static(render_result_label(rank, result, self._all_results)))
            )
        if visible:
            list_view.index = 0

    def _selected_result(self) -> Optional[SearchResult]:
        list_view = self.query_one("#results", ListView)
        index = list_view.index
        if index is None or index < 0:
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

    def _refresh_results_ui(self) -> None:
        self.query_one("#header", Static).update(self._header_text())
        self._update_banner()
        self._refresh_list()

    def _copy_selected(self) -> None:
        result = self._selected_result()
        if result is None:
            return
        text = matched_commands_text(result)
        self.copy_to_clipboard(text)
        self.notify("Copied to clipboard", title="whatwasit", timeout=2)

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


class WhatwasitTUI(_ResultPanelMixin, App[None]):
    """Browse pre-fetched search results (one-shot ``whatwasit "query"``)."""

    CSS = """
    Screen {
        layout: vertical;
    }
    #banner {
        height: auto;
        padding: 0 1;
        display: none;
    }
    #results {
        height: 1fr;
        border: solid $accent;
        margin: 0 1;
    }
    #status {
        height: auto;
        padding: 0 1;
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("down", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("up", "cursor_up", "Up"),
        Binding("n", "load_more", "More"),
    ]

    def __init__(
        self,
        results: List[SearchResult],
        query: str,
        *,
        page_size: int = 5,
        low_confidence_threshold: float = 0.40,
    ) -> None:
        super().__init__()
        self._all_results = results
        self._query = query
        self._page_size = max(1, page_size)
        self._visible_count = min(self._page_size, len(results))
        self._low_confidence_threshold = low_confidence_threshold

    def compose(self) -> ComposeResult:
        yield Static(self._header_text(), id="header")
        yield Static("", id="banner")
        yield ListView(id="results")
        yield Static(
            "Enter copy  n more  j/k navigate  q quit",
            id="status",
        )
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_results_ui()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self._copy_selected()


class WhatwasitREPL(_ResultPanelMixin, App[None]):
    """Persistent interactive REPL launched by bare ``whatwasit``."""

    CSS = """
    Screen {
        layout: vertical;
    }
    #banner {
        height: auto;
        padding: 0 1;
        display: none;
    }
    #results {
        height: 1fr;
        border: solid $accent;
        margin: 0 1;
    }
    #prompt {
        dock: bottom;
        margin: 0 1 1 1;
        border: tall $accent;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("down", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("up", "cursor_up", "Up"),
        Binding("n", "load_more", "More"),
        Binding("ctrl+c", "quit", "Quit", show=False),
    ]

    def __init__(
        self,
        search_fn: Callable[[str], List[SearchResult]],
        *,
        page_size: int = 5,
        low_confidence_threshold: float = 0.40,
    ) -> None:
        super().__init__()
        self._search_fn = search_fn
        self._all_results: List[SearchResult] = []
        self._query = ""
        self._page_size = max(1, page_size)
        self._visible_count = 0
        self._low_confidence_threshold = low_confidence_threshold

    def compose(self) -> ComposeResult:
        yield Static(f"{CLI_NAME} — type a query or /help", id="header")
        yield Static("", id="banner")
        yield ListView(id="results")
        yield Input(placeholder="Search shell history…  (/help for commands)", id="prompt")

    def on_mount(self) -> None:
        self.query_one("#prompt", Input).focus()

    def _run_query(self, query: str) -> None:
        self._query = query
        self._all_results = self._search_fn(query)
        self._visible_count = min(self._page_size, len(self._all_results))
        self._refresh_results_ui()

    def _handle_slash(self, raw: str) -> None:
        cmd = raw.strip().lower()
        if cmd in ("/quit", "/q", "/exit"):
            self.exit()
            return
        if cmd == "/help":
            self.action_show_help()
            return
        if cmd == "/more":
            self.action_load_more()
            return
        self.notify(f"Unknown command: {raw!r} — try /help", severity="warning", timeout=3)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        event.input.value = ""
        if not value:
            return
        if value.startswith("/"):
            self._handle_slash(value)
            return
        self._run_query(value)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self._copy_selected()


def run_tui(
    results: List[SearchResult],
    query: str,
    *,
    page_size: int = 5,
    low_confidence_threshold: float = 0.40,
) -> None:
    """Launch the one-shot interactive TUI (blocking)."""
    WhatwasitTUI(
        results,
        query,
        page_size=page_size,
        low_confidence_threshold=low_confidence_threshold,
    ).run()


def run_repl(
    search_fn: Callable[[str], List[SearchResult]],
    *,
    page_size: int = 5,
    low_confidence_threshold: float = 0.40,
) -> None:
    """Launch the persistent REPL (blocking)."""
    WhatwasitREPL(
        search_fn,
        page_size=page_size,
        low_confidence_threshold=low_confidence_threshold,
    ).run()
