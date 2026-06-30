"""Rich-formatted rendering of search results for the CLI.

Turns a list of :class:`hist.models.SearchResult` into a readable terminal
report: one panel per result, with the matched command(s) highlighted and
the surrounding commands dimmed for context.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .models import SearchResult


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
                title="hist",
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
