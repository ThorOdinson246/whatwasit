"""Small string helpers for search and display."""

from __future__ import annotations

DISPLAY_CMD_MAX_CHARS = 96
EMBED_CMD_MAX_CHARS = 512


def truncate_display(text: str, *, max_chars: int = DISPLAY_CMD_MAX_CHARS) -> str:
    """Truncate command text for TUI rows."""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "…"


def truncate_for_embed(text: str, *, max_chars: int = EMBED_CMD_MAX_CHARS) -> str:
    """Truncate command text before embedding to avoid pathological latency."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars]
