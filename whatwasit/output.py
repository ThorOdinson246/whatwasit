"""Rendering search results for plain and interactive output modes.

Plain mode prints Rich panels (or line-oriented text when not a TTY).
TUI mode delegates to :mod:`whatwasit.tui`.
"""

from __future__ import annotations

import json
import sys
from typing import List, Optional, TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .models import SearchResult
from .config_loader import config_file_path
from .timefmt import format_relative_time, format_timestamp
from .tui import confidence_level, low_confidence_message, render_result_label

if TYPE_CHECKING:
    from .config import Config


def _render_commands(session, matched_indices: List[int]) -> Text:
    """Build a Text block listing a session's commands in order."""
    matched = set(matched_indices)
    text = Text()
    for i, command in enumerate(session.commands):
        if i in matched:
            text.append("  › ", style="bold")
            text.append(f"{command.raw_cmd}\n", style="bold")
        else:
            text.append("    ", style="dim")
            text.append(f"{command.raw_cmd}\n", style="dim")
    return text


def render_results(
    results: List[SearchResult],
    query: str,
    console: Optional[Console] = None,
    *,
    low_confidence_threshold: float = 0.40,
) -> None:
    """Print ``results`` for ``query`` to the terminal using rich."""
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

    banner = low_confidence_message(results, low_confidence_threshold)
    if banner:
        console.print(Text(banner, style="bold yellow"))

    console.print(Text(f'Results for: "{query}"', style="bold underline"))
    for rank, result in enumerate(results, start=1):
        session = result.session
        level = confidence_level(result, rank, results)
        header = render_result_label(result, results, rank)
        body = Text()
        body.append(f"{session.cwd or '?'}\n", style="dim")
        body.append_text(_render_commands(session, result.matched_indices))
        border = "yellow" if level == "weak" else "bright_black"
        console.print(Panel(body, title=header, border_style=border))


def render_plain_lines(
    results: List[SearchResult],
    query: str,
    *,
    file=None,
    low_confidence_threshold: float = 0.40,
) -> None:
    """Line-oriented plain output suitable for piping."""
    out = file if file is not None else sys.stdout
    if not results:
        print(f'No results found for: "{query}"', file=out)
        return

    banner = low_confidence_message(results, low_confidence_threshold)
    if banner:
        print(banner, file=out)

    print(f'Results for: "{query}"', file=out)
    for rank, result in enumerate(results, start=1):
        session = result.session
        weak = confidence_level(result, rank, results) == "weak"
        flag = " !" if weak else ""
        print(
            f"#{rank}\tscore={result.score:.2f}{flag}\t"
            f"{format_relative_time(session.start_ts)}\t{session.cwd or '?'}",
            file=out,
        )
        matched = set(result.matched_indices)
        for i, command in enumerate(session.commands):
            marker = ">" if i in matched else " "
            print(f"  {marker} {command.raw_cmd}", file=out)
        print(file=out)


def render_json(
    results: List[SearchResult],
    query: str,
    *,
    low_confidence_threshold: float = 0.40,
) -> str:
    """Serialize search results for scripting (``--json``)."""
    banner = low_confidence_message(results, low_confidence_threshold)
    payload = {
        "query": query,
        "count": len(results),
        "low_confidence": banner is not None,
        "low_confidence_message": banner,
        "results": [
            {
                "rank": rank,
                "score": round(result.score, 6),
                "confidence": confidence_level(result, rank, results),
                "session": {
                    "id": result.session.id,
                    "cwd": result.session.cwd,
                    "start_ts": result.session.start_ts,
                    "start_relative": format_relative_time(result.session.start_ts),
                },
                "matched_indices": result.matched_indices,
                "commands": [cmd.raw_cmd for cmd in result.session.commands],
            }
            for rank, result in enumerate(results, start=1)
        ],
    }
    return json.dumps(payload, indent=2)


def display_results(
    results: List[SearchResult],
    query: str,
    config: "Config",
    *,
    force_plain: bool = False,
    console: Optional[Console] = None,
) -> None:
    """Render *results* using the configured output mode."""
    threshold = config.low_confidence_threshold
    use_plain = force_plain or config.output_mode == "plain"

    if use_plain:
        if console is not None or sys.stdout.isatty():
            render_results(
                results,
                query,
                console=console,
                low_confidence_threshold=threshold,
            )
        else:
            render_plain_lines(
                results,
                query,
                low_confidence_threshold=threshold,
            )
        return

    if not sys.stdout.isatty():
        render_plain_lines(results, query, low_confidence_threshold=threshold)
        return

    from .tui import run_tui

    run_tui(
        results,
        query,
        page_size=config.tui_page_size,
        low_confidence_threshold=threshold,
        theme=config.tui_theme,
        output_mode=config.output_mode,
        config_path=str(config_file_path()),
    )
