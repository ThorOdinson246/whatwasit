"""JSONL and raw-command helpers for eval datasets.

The production package does not import this module. It exists to keep eval
authoring, external raw-data conversion, and validation deterministic.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


PROMPT_RE = re.compile(r"^\s*(?:\$|%|>)\s+")


@dataclass(frozen=True)
class DatasetStats:
    sessions: int
    queries: int
    answerable: int
    null: int


def load_jsonl(path: Path | str) -> list[dict]:
    p = Path(path)
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def write_jsonl(path: Path | str, rows: Iterable[dict]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def validate_sessions(sessions: Sequence[dict]) -> None:
    seen: set[str] = set()
    for row in sessions:
        sid = row.get("session_id")
        if not isinstance(sid, str) or not sid:
            raise ValueError("session row missing non-empty session_id")
        if sid in seen:
            raise ValueError(f"duplicate session_id: {sid}")
        seen.add(sid)
        if not isinstance(row.get("topic"), str) or not row["topic"]:
            raise ValueError(f"{sid}: missing topic")
        if not isinstance(row.get("cwd"), str) or not row["cwd"]:
            raise ValueError(f"{sid}: missing cwd")
        commands = row.get("commands")
        if not isinstance(commands, list) or not commands:
            raise ValueError(f"{sid}: commands must be a non-empty list")
        if any(not isinstance(cmd, str) or not cmd.strip() for cmd in commands):
            raise ValueError(f"{sid}: commands must be non-empty strings")


def validate_queries(queries: Sequence[dict], session_ids: set[str]) -> None:
    seen: set[str] = set()
    for i, row in enumerate(queries):
        qid = row.get("query_id", f"query_{i:04d}")
        if not isinstance(qid, str) or not qid:
            raise ValueError("query row has invalid query_id")
        if qid in seen:
            raise ValueError(f"duplicate query_id: {qid}")
        seen.add(qid)
        if not isinstance(row.get("query"), str) or not row["query"].strip():
            raise ValueError(f"{qid}: missing query")
        if not isinstance(row.get("topic"), str) or not row["topic"]:
            raise ValueError(f"{qid}: missing topic")
        gold = row.get("correct_session_id")
        if gold is not None and gold not in session_ids:
            raise ValueError(f"{qid}: unknown correct_session_id {gold!r}")


def dataset_stats(sessions: Sequence[dict], queries: Sequence[dict]) -> DatasetStats:
    answerable = sum(1 for row in queries if row.get("correct_session_id") is not None)
    return DatasetStats(
        sessions=len(sessions),
        queries=len(queries),
        answerable=answerable,
        null=len(queries) - answerable,
    )


def normalize_raw_command(line: str) -> str | None:
    """Normalize one raw command line, returning ``None`` for unusable rows."""
    cmd = PROMPT_RE.sub("", line.strip())
    if not cmd:
        return None
    if cmd.startswith("#"):
        return None
    if len(cmd) < 4 or len(cmd) > 240:
        return None
    if cmd.lower() in {"clear", "history", "exit", "logout"}:
        return None
    return cmd


def load_raw_commands(paths: Sequence[Path | str]) -> list[str]:
    commands: list[str] = []
    seen: set[str] = set()
    for path in paths:
        for line in Path(path).read_text(errors="ignore").splitlines():
            cmd = normalize_raw_command(line)
            if cmd is None or cmd in seen:
                continue
            seen.add(cmd)
            commands.append(cmd)
    return commands


def raw_commands_to_sessions(
    commands: Sequence[str],
    *,
    suite: str,
    source: str,
    session_size: int = 5,
    limit: int | None = None,
    cwd_prefix: str = "~/external",
) -> list[dict]:
    """Group normalized commands into deterministic synthetic sessions."""
    if session_size <= 0:
        raise ValueError("session_size must be positive")
    selected = list(commands[:limit]) if limit is not None else list(commands)
    sessions: list[dict] = []
    for idx in range(0, len(selected), session_size):
        chunk = selected[idx : idx + session_size]
        if not chunk:
            continue
        sid = f"{suite}_{len(sessions):04d}"
        sessions.append(
            {
                "session_id": sid,
                "topic": "external-raw",
                "cwd": f"{cwd_prefix}/{source}",
                "commands": chunk,
                "provenance": {"source": source, "kind": "raw-command-sample"},
            }
        )
    return sessions
