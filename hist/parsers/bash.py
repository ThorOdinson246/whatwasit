"""Parser for bash history files.

Plain ``.bash_history`` files are just one command per line. When
``HISTTIMEFORMAT`` is set, bash prepends each command with a comment line of
the form ``#<epoch>`` holding the timestamp for the command that follows.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from ..models import Command


def parse_bash(path: Path | str) -> List[Command]:
    """Parse a bash history file into a list of :class:`Command`.

    Malformed or unreadable input never raises; offending lines are skipped.
    """
    commands: List[Command] = []

    try:
        text = Path(path).read_text(errors="replace")
    except OSError:
        return commands

    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()

    pending_ts: Optional[int] = None
    for line in lines:
        try:
            if line.startswith("#"):
                ts_str = line[1:].strip()
                if ts_str.isdigit():
                    pending_ts = int(ts_str)
                else:
                    pending_ts = None
                continue

            if line.strip() == "":
                pending_ts = None
                continue

            commands.append(Command(raw_cmd=line, ts=pending_ts, source="bash"))
            pending_ts = None
        except Exception:
            pending_ts = None
            continue

    return commands
