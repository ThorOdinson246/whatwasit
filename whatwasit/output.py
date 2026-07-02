"""Rendering search results for plain and interactive output modes.

Plain mode prints Rich panels (or line-oriented text when not a TTY).
TUI mode delegates to :mod:`whatwasit.tui`.
"""

from __future__ import annotations

import sys
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .models import SearchResult

if TYPE_CHECKING:
    from .config import Config


def format_timestamp(ts: Optional[int]) -> str:
    """Render a unix-epoch timestamp as a human-readable local datetime.

    Returns ``"unknown"`` if ``ts`` is ``None``.
    """
    if ts is None:
        return "unknown"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def _render_commands(session, matched_indices: List[int]) -> Text:
    """Build a Text block listing a session's commands in order.

    Commands at ``matched_indices`` are highlighted (bold, with a marker);
    all other commands are dimmed as surrounding context.
    """
    matched = set(matched_indices)
    text = Text()
    for i, command in enumerate(session.commands):
        if i in matched:
            text.append("  > ", style="bold green")
            text.append(f"{command.raw_cmd}\n", style="bold green")
        else:
            text.append("    ", style="dim")
            text.append(f"{command.raw_cmd}\n", style="dim")
    return text


def render_results(
    results: List[SearchResult],
    query: str,
    console: Optional[Console] = None,
) -> None:
    """Print ``results`` for ``query`` to the terminal using rich.

    Each result is shown as a panel with its rank, similarity score, the
    session's start timestamp, working directory, and its commands (with
    the matched ones highlighted). Prints a friendly message if ``results``
    is empty.
    """
    if console is None:
        console = Console()

    if not results:
        console.print(
            Panel(
                Text(f"No results found for: {query!r}", style="italic"),
                title="whatwasit",
                border_style="yellow",
            )
        )
        return

    console.print(Text(f'Results for: "{query}"', style="bold underline"))
    for rank, result in enumerate(results, start=1):
        session = result.session
        header = Text()
        header.append(f"#{rank}  ", style="bold")
        header.append(f"score={result.score:.2f}", style="cyan")
        header.append("  ")
        header.append(format_timestamp(session.start_ts), style="magenta")
        header.append("  ")
        header.append(session.cwd or "?", style="bold blue")

        body = _render_commands(session, result.matched_indices)

        console.print(Panel(body, title=header, border_style="bright_black"))


def render_plain_lines(
    results: List[SearchResult],
    query: str,
    *,
    file=None,
) -> None:
    """Line-oriented plain output suitable for piping."""
    out = file if file is not None else sys.stdout
    if not results:
        print(f'No results found for: "{query}"', file=out)
        return

    print(f'Results for: "{query}"', file=out)
    for rank, result in enumerate(results, start=1):
        session = result.session
        print(
            f"#{rank}\tscore={result.score:.2f}\t"
            f"{format_timestamp(session.start_ts)}\t{session.cwd or '?'}",
            file=out,
        )
        matched = set(result.matched_indices)
        for i, command in enumerate(session.commands):
            marker = ">" if i in matched else " "
            print(f"  {marker} {command.raw_cmd}", file=out)
        print(file=out)


def display_results(
    results: List[SearchResult],
    query: str,
    config: "Config",
    *,
    force_plain: bool = False,
    console: Optional[Console] = None,
) -> None:
    """Render *results* using the configured output mode."""
    use_plain = force_plain or config.output_mode == "plain"

    if use_plain:
        if console is not None or sys.stdout.isatty():
            render_results(results, query, console=console)
        else:
            render_plain_lines(results, query)
        return

    from .tui import run_tui

    run_tui(
        results,
        query,
        page_size=config.tui_page_size,
        low_confidence_threshold=config.low_confidence_threshold,
    )
