"""Copy text to the system clipboard with sensible Linux fallbacks."""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Iterable, List

# Avoid feeding megabyte paste-bombs to clipboard helpers.
_MAX_CLIPBOARD_BYTES = 512_000


def _clipboard_commands() -> Iterable[List[str]]:
    if os.environ.get("WAYLAND_DISPLAY"):
        yield ["wl-copy"]
    yield ["xclip", "-selection", "clipboard"]
    yield ["xsel", "--clipboard", "--input"]
    yield ["clip"]


def copy_to_clipboard(text: str) -> bool:
    """Copy *text* to the system clipboard. Returns True on success."""
    if not text:
        return False

    payload = text.encode("utf-8")
    if len(payload) > _MAX_CLIPBOARD_BYTES:
        payload = payload[:_MAX_CLIPBOARD_BYTES]

    for cmd in _clipboard_commands():
        if shutil.which(cmd[0]) is None:
            continue
        try:
            subprocess.run(
                cmd,
                input=payload,
                check=True,
                timeout=2,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except (OSError, subprocess.SubprocessError):
            continue
    return False
