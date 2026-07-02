"""Parser for atuin's SQLite history database.

Atuin stores ``timestamp`` as nanoseconds since the epoch; everything else in
``whatwasit`` deals in whole seconds, so it is converted here. The database is
opened read-only so this module can never mutate the user's atuin history.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List, Optional

from ..models import Command

_NANOS_PER_SECOND = 1_000_000_000

# Columns commonly present in atuin's `history` table. Only the ones that
# actually exist in a given database are selected.
_DESIRED_COLUMNS = ["timestamp", "duration", "exit", "command", "cwd"]


def parse_atuin(db_path: Path | str) -> List[Command]:
    """Parse atuin's history database into a list of :class:`Command`.

    Opens the database read-only. Tolerates missing columns/tables and never
    raises on malformed rows; offending rows are skipped.
    """
    commands: List[Command] = []

    path = Path(db_path)
    if not path.exists():
        return commands

    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
    except sqlite3.Error:
        return commands

    try:
        try:
            cols_info = conn.execute("PRAGMA table_info(history)").fetchall()
        except sqlite3.Error:
            return commands

        available = {row[1] for row in cols_info}
        if "command" not in available:
            return commands

        select_cols = [c for c in _DESIRED_COLUMNS if c in available]
        if "command" not in select_cols:
            return commands

        query = f"SELECT {', '.join(select_cols)} FROM history"  # noqa: S608
        try:
            rows = conn.execute(query).fetchall()
        except sqlite3.Error:
            return commands

        for row in rows:
            try:
                data = dict(row)
                raw_cmd = data.get("command")
                if raw_cmd is None:
                    continue

                ts_ns = data.get("timestamp")
                ts: Optional[int] = (
                    int(ts_ns) // _NANOS_PER_SECOND if ts_ns is not None else None
                )

                duration_raw = data.get("duration")
                duration = int(duration_raw) if duration_raw is not None else None

                exit_raw = data.get("exit")
                exit_code = int(exit_raw) if exit_raw is not None else None

                cwd = data.get("cwd")

                commands.append(
                    Command(
                        raw_cmd=raw_cmd,
                        ts=ts,
                        source="atuin",
                        cwd=cwd,
                        duration=duration,
                        exit_code=exit_code,
                    )
                )
            except Exception:
                continue
    finally:
        conn.close()

    return commands
