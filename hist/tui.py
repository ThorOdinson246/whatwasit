"""Interactive Textual TUI for browsing search results."""

from __future__ import annotations

from typing import List, Optional

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.events import Key
from textual.widgets import Footer, ListItem, ListView, Static

from .models import SearchResult
from .output import format_timestamp


def _format_result_label(rank: int, result: SearchResult) -> str:
    session = result.session
    cwd = session.cwd or "?"
    ts = format_timestamp(session.start_ts)
    return f"#{rank}  score={result.score:.2f}  {ts}  {cwd}"


def _render_commands_text(result: SearchResult) -> Text:
    """Build Rich text for a session's commands, highlighting matches."""
    matched = set(result.matched_indices)
    text = Text()
    for i, command in enumerate(result.session.commands):
        if i in matched:
            text.append("  > ", style="bold green")
            text.append(f"{command.raw_cmd}\n", style="bold green")
        else:
            text.append("    ", style="dim")
            text.append(f"{command.raw_cmd}\n", style="dim")
    return text


class HistTUI(App[None]):
    """Browse search results interactively."""

    CSS = """
    #detail {
        height: 1fr;
        border: solid $accent;
        padding: 1 2;
        margin-top: 1;
    }
    ListView {
        height: auto;
        max-height: 12;
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
    ) -> None:
        super().__init__()
        self._all_results = results
        self._query = query
        self._page_size = max(1, page_size)
        self._visible_count = min(self._page_size, len(results))
        self._expanded = False

    def compose(self) -> ComposeResult:
        yield Static(self._header_text(), id="header")
        yield ListView(id="results")
        yield Static("", id="detail")
        yield Footer()

    def _header_text(self) -> str:
        if not self._all_results:
            return f'No results for: "{self._query}"'
        shown = min(self._visible_count, len(self._all_results))
        total = len(self._all_results)
        return f'Results for: "{self._query}" ({shown}/{total})'

    def on_mount(self) -> None:
        self._refresh_list()
        self._update_detail()

    def _refresh_list(self) -> None:
        list_view = self.query_one("#results", ListView)
        list_view.clear()
        visible = self._all_results[: self._visible_count]
        for rank, result in enumerate(visible, start=1):
            list_view.append(ListItem(Static(_format_result_label(rank, result))))
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

    def _update_detail(self) -> None:
        detail = self.query_one("#detail", Static)
        if not self._expanded:
            detail.update(
                "[dim]Enter[/] expand session  "
                "[dim]n[/] more  "
                "[dim]j/k[/] or arrows navigate  "
                "[dim]q[/] quit"
            )
            return
        result = self._selected_result()
        if result is None:
            detail.update("")
            return
        detail.update(_render_commands_text(result))

    def action_cursor_down(self) -> None:
        list_view = self.query_one("#results", ListView)
        if list_view.index is not None and list_view.index < len(list_view.children) - 1:
            list_view.index += 1
        self._expanded = False
        self._update_detail()

    def action_cursor_up(self) -> None:
        list_view = self.query_one("#results", ListView)
        if list_view.index is not None and list_view.index > 0:
            list_view.index -= 1
        self._expanded = False
        self._update_detail()

    def action_load_more(self) -> None:
        if self._visible_count >= len(self._all_results):
            return
        self._visible_count = min(
            self._visible_count + self._page_size,
            len(self._all_results),
        )
        self.query_one("#header", Static).update(self._header_text())
        self._refresh_list()
        self._expanded = False
        self._update_detail()

    def action_toggle_expand(self) -> None:
        self._expanded = not self._expanded
        self._update_detail()

    def on_key(self, event: Key) -> None:
        if event.key == "enter":
            self.action_toggle_expand()
            event.prevent_default()
            event.stop()


def run_tui(
    results: List[SearchResult],
    query: str,
    *,
    page_size: int = 5,
) -> None:
    """Launch the interactive TUI (blocking)."""
    HistTUI(results, query, page_size=page_size).run()
