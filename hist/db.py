"""SQLite persistence layer: schema, migrations stub, and CRUD.

This module owns the database schema and all low-level reads/writes for the
``meta``, ``commands``, and ``sessions`` tables. The vector data itself lives in
a separate usearch file managed by ``hist.index``; this DB stores the session
metadata and command text those vector keys point back to.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterator, List, Optional

from .config import SCHEMA_VERSION
from .models import Command, Session

_SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    start_ts      INTEGER,
    end_ts        INTEGER,
    cwd           TEXT,
    command_count INTEGER NOT NULL DEFAULT 0,
    doc_text      TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS commands (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    seq        INTEGER NOT NULL,
    source     TEXT,
    ts         INTEGER,
    duration   INTEGER,
    exit_code  INTEGER,
    cwd        TEXT,
    raw_cmd    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_commands_session ON commands(session_id);
"""


def connect(path: Path | str) -> sqlite3.Connection:
    """Open (creating the parent dir if needed) a SQLite connection."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize(conn: sqlite3.Connection) -> None:
    """Create tables and stamp the schema version if not already present."""
    conn.executescript(_SCHEMA)
    cur = conn.execute("SELECT value FROM meta WHERE key = 'schema_version'")
    row = cur.fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO meta(key, value) VALUES ('schema_version', ?)",
            (str(SCHEMA_VERSION),),
        )
    conn.commit()


def get_schema_version(conn: sqlite3.Connection) -> Optional[int]:
    cur = conn.execute("SELECT value FROM meta WHERE key = 'schema_version'")
    row = cur.fetchone()
    return int(row["value"]) if row else None


def get_meta(conn: sqlite3.Connection, key: str) -> Optional[str]:
    """Return a value from the ``meta`` table, or ``None`` if absent."""
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    """Insert or replace a ``meta`` table entry."""
    conn.execute(
        "INSERT INTO meta(key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


def reset(conn: sqlite3.Connection) -> None:
    """Drop all data tables (used for a full re-index) and recreate them."""
    conn.executescript(
        "DROP TABLE IF EXISTS commands;"
        "DROP TABLE IF EXISTS sessions;"
        "DROP TABLE IF EXISTS meta;"
    )
    conn.commit()
    initialize(conn)


def insert_session(conn: sqlite3.Connection, session: Session) -> int:
    """Insert a session and its commands. Returns the new session id."""
    doc_text = session.doc_text if session.doc_text is not None else session.to_document()
    cur = conn.execute(
        "INSERT INTO sessions(start_ts, end_ts, cwd, command_count, doc_text) "
        "VALUES (?, ?, ?, ?, ?)",
        (session.start_ts, session.end_ts, session.cwd, session.command_count, doc_text),
    )
    session_id = int(cur.lastrowid)
    conn.executemany(
        "INSERT INTO commands(session_id, seq, source, ts, duration, exit_code, cwd, raw_cmd) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                session_id,
                seq,
                c.source,
                c.ts,
                c.duration,
                c.exit_code,
                c.cwd,
                c.raw_cmd,
            )
            for seq, c in enumerate(session.commands)
        ],
    )
    session.id = session_id
    return session_id


def _row_to_command(row: sqlite3.Row) -> Command:
    return Command(
        raw_cmd=row["raw_cmd"],
        ts=row["ts"],
        source=row["source"] or "unknown",
        cwd=row["cwd"],
        duration=row["duration"],
        exit_code=row["exit_code"],
    )


def get_session(conn: sqlite3.Connection, session_id: int) -> Optional[Session]:
    """Load a single session (with commands ordered by seq)."""
    srow = conn.execute(
        "SELECT * FROM sessions WHERE id = ?", (session_id,)
    ).fetchone()
    if srow is None:
        return None
    crows = conn.execute(
        "SELECT * FROM commands WHERE session_id = ? ORDER BY seq", (session_id,)
    ).fetchall()
    return Session(
        id=srow["id"],
        start_ts=srow["start_ts"],
        end_ts=srow["end_ts"],
        cwd=srow["cwd"],
        doc_text=srow["doc_text"],
        commands=[_row_to_command(r) for r in crows],
    )


def iter_sessions(conn: sqlite3.Connection) -> Iterator[Session]:
    """Yield every stored session (with commands), ordered by id."""
    for srow in conn.execute("SELECT id FROM sessions ORDER BY id").fetchall():
        s = get_session(conn, int(srow["id"]))
        if s is not None:
            yield s


def count_sessions(conn: sqlite3.Connection) -> int:
    return int(conn.execute("SELECT COUNT(*) AS n FROM sessions").fetchone()["n"])
