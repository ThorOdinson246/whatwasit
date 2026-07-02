"""Parser for zsh history files (plain and ``EXTENDED_HISTORY`` formats).

EXTENDED_HISTORY entries look like::

    : <epoch>:<duration>;<command>

Plain entries are just the raw command text with no metadata prefix. Either
form may span multiple physical lines when the command itself contains a
backslash-continued newline, in which case zsh writes the continuation as a
trailing ``\\`` at the end of the physical line.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from ..models import Command

_EXTENDED_RE = re.compile(r"^: (\d+):(\d+);(.*)$")


def parse_zsh(path: Path | str) -> List[Command]:
    """Parse a zsh history file into a list of :class:`Command`.

    Malformed or unreadable input never raises; offending lines are skipped.
    """
    commands: List[Command] = []

    try:
        text = Path(path).read_text(errors="replace")
    except OSError:
        return commands

    raw_lines = text.split("\n")
    if raw_lines and raw_lines[-1] == "":
        raw_lines.pop()

    n = len(raw_lines)
    i = 0
    while i < n:
        line = raw_lines[i]
        try:
            ts: Optional[int] = None
            duration: Optional[int] = None

            match = _EXTENDED_RE.match(line)
            if match:
                ts = int(match.group(1))
                duration = int(match.group(2))
                body = match.group(3)
            else:
                body = line

            parts = [body]
            while parts[-1].endswith("\\"):
                i += 1
                if i >= n:
                    parts[-1] = parts[-1][:-1]
                    break
                parts[-1] = parts[-1][:-1]
                parts.append(raw_lines[i])

            cmd_text = "\n".join(parts)
            if cmd_text.strip() == "":
                i += 1
                continue

            commands.append(
                Command(raw_cmd=cmd_text, ts=ts, duration=duration, source="zsh")
            )
        except Exception:
            # Malformed line/record: skip and keep going.
            pass
        i += 1

    return commands
