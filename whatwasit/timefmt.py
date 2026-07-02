"""Human-readable time formatting for CLI and TUI output."""

from __future__ import annotations

from datetime import datetime
from typing import Optional


def format_timestamp(ts: Optional[int]) -> str:
    """Render a unix-epoch timestamp as a local datetime string."""
    if ts is None:
        return "unknown"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def format_relative_time(ts: Optional[int], *, now: Optional[datetime] = None) -> str:
    """Render a unix-epoch timestamp as a compact relative time (e.g. ``3h ago``)."""
    if ts is None:
        return "unknown"
    reference = now or datetime.now()
    then = datetime.fromtimestamp(ts)
    seconds = max(0, int((reference - then).total_seconds()))
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    if seconds < 86400:
        return f"{seconds // 3600}h ago"
    if seconds < 604800:
        return f"{seconds // 86400}d ago"
    if seconds < 2_592_000:
        return f"{seconds // 604800}w ago"
    return then.strftime("%Y-%m-%d")
