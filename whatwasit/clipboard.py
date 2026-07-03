"""Copy text to the system clipboard with sensible Linux fallbacks."""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Iterable, List


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

    for cmd in _clipboard_commands():
        if shutil.which(cmd[0]) is None:
            continue
        try:
            subprocess.run(
                cmd,
                input=text.encode("utf-8"),
                check=True,
                timeout=2,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except (OSError, subprocess.SubprocessError):
            continue
    return False
