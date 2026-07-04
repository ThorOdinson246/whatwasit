"""Private personal eval workflow.

This module creates and validates local-only eval files under ``eval/private``.
It must never write real shell history into tracked paths.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from eval.dataset_io import load_jsonl, validate_queries, validate_sessions, write_jsonl
from whatwasit import db
from whatwasit.config import Config


EVAL_DIR = Path(__file__).resolve().parent
DEFAULT_DIR = EVAL_DIR / "private" / "personal"
SECRET_PATTERNS = [
    re.compile(r"password\s*=", re.IGNORECASE),
    re.compile(r"token\s*=", re.IGNORECASE),
    re.compile(r"aws_secret", re.IGNORECASE),
    re.compile(r"bearer\s+[a-z0-9._~+/=-]{20,}", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]
NOISE_COMMANDS = {"cd", "ls", "clear", "cls", "exit", "logout", "pwd", "history"}
TOOL_TOPICS = {
    "git": "git",
    "docker": "docker",
    "docker-compose": "docker",
    "ssh": "ssh",
    "scp": "ssh",
    "rsync": "sync",
    "python": "python",
    "python3": "python",
    "pip": "python",
    "pytest": "python",
    "npm": "javascript",
    "node": "javascript",
    "curl": "http",
    "wget": "download",
    "nginx": "nginx",
    "systemctl": "systemd",
    "journalctl": "logs",
    "sudo": "system",
    "apt": "packages",
    "apt-get": "packages",
    "warp-cli": "network",
    "code": "editor",
    "vscode": "editor",
    "nano": "editor",
    "chmod": "permissions",
    "chown": "permissions",
}


def likely_secret(text: str) -> bool:
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def personal_paths(root: Path = DEFAULT_DIR) -> dict[str, Path]:
    return {
        "root": root,
        "sessions": root / "sessions.jsonl",
        "queries": root / "queries.jsonl",
        "candidates": root / "candidates.jsonl",
        "baselines": root / "baselines",
        "runs": root / "runs",
    }


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _ensure_private_path(path: Path) -> None:
    private_root = EVAL_DIR / "private"
    if not _is_relative_to(path, private_root):
        raise SystemExit(f"refusing to write private history outside {private_root}: {path}")


def init_personal(root: Path = DEFAULT_DIR) -> None:
    paths = personal_paths(root)
    paths["baselines"].mkdir(parents=True, exist_ok=True)
    paths["runs"].mkdir(parents=True, exist_ok=True)
    paths["root"].mkdir(parents=True, exist_ok=True)
    for key in ("sessions", "queries"):
        paths[key].touch(exist_ok=True)
    print(f"initialized {paths['root']}")


def _session_to_row(session, *, prefix: str, index: int) -> dict:
    return {
        "session_id": f"{prefix}_{index:06d}",
        "topic": "unlabeled",
        "cwd": session.cwd or "?",
        "commands": [cmd.raw_cmd for cmd in session.commands],
        "provenance": {
            "source": "local-whatwasit-db",
            "db_session_id": session.id,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "private": True,
        },
    }


def export_candidates(
    db_path: Path,
    out: Path,
    *,
    limit: int,
    prefix: str = "personal",
    allow_unsafe_path: bool = False,
) -> None:
    if not allow_unsafe_path:
        _ensure_private_path(out)
    conn = db.connect(db_path)
    try:
        db.initialize(conn)
        rows = []
        for idx, session in enumerate(db.iter_sessions(conn)):
            if idx >= limit:
                break
            rows.append(_session_to_row(session, prefix=prefix, index=idx))
    finally:
        conn.close()
    write_jsonl(out, rows)
    print(f"exported {len(rows)} candidates to {out}")


def _read_existing(path: Path) -> list[dict]:
    return load_jsonl(path) if path.exists() else []


def _validate_personal_rows(
    sessions: list[dict],
    queries: list[dict],
    *,
    strict_size: bool = False,
) -> tuple[int, int]:
    validate_sessions(sessions)
    validate_queries(queries, {row["session_id"] for row in sessions})

    for row in sessions:
        combined = "\n".join([row.get("cwd", ""), *row.get("commands", [])])
        if likely_secret(combined):
            raise SystemExit(f"likely secret in session {row['session_id']}")
    for row in queries:
        if likely_secret(row.get("query", "")):
            raise SystemExit(f"likely secret in query {row.get('query_id', row.get('query'))}")
        if row.get("correct_session_id") is None and row.get("kind") not in {None, "null"}:
            raise SystemExit(f"null query must use kind=null: {row.get('query_id')}")

    if strict_size:
        answerable = sum(1 for row in queries if row.get("correct_session_id") is not None)
        nulls = len(queries) - answerable
        if len(sessions) < 50 or answerable < 100 or nulls < 15:
            raise SystemExit(
                "personal suite is below promotion-gate size "
                f"({len(sessions)} sessions, {answerable} answerable, {nulls} null)"
            )
    print(f"valid personal suite: {len(sessions)} sessions, {len(queries)} queries")
    return len(sessions), len(queries)


def validate_personal(root: Path = DEFAULT_DIR, *, strict_size: bool = False) -> tuple[int, int]:
    paths = personal_paths(root)
    return _validate_personal_rows(
        _read_existing(paths["sessions"]),
        _read_existing(paths["queries"]),
        strict_size=strict_size,
    )


def status_personal(root: Path = DEFAULT_DIR) -> dict[str, int]:
    paths = personal_paths(root)
    counts = {
        "candidates": len(_read_existing(paths["candidates"])),
        "sessions": len(_read_existing(paths["sessions"])),
        "queries": len(_read_existing(paths["queries"])),
    }
    answerable = sum(
        1
        for row in _read_existing(paths["queries"])
        if row.get("correct_session_id") is not None
    )
    counts["answerable"] = answerable
    counts["null"] = counts["queries"] - answerable
    print(
        "personal eval status: "
        f"{counts['candidates']} candidates, "
        f"{counts['sessions']} labeled sessions, "
        f"{counts['answerable']} answerable queries, "
        f"{counts['null']} null queries"
    )
    return counts


def _append_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _next_query_index(rows: Sequence[dict]) -> int:
    max_seen = -1
    for row in rows:
        qid = str(row.get("query_id", ""))
        match = re.fullmatch(r"personal_q(\d+)", qid)
        if match:
            max_seen = max(max_seen, int(match.group(1)))
    return max_seen + 1


def _redact_row(row: dict, needle: str, replacement: str = "[REDACTED]") -> dict:
    redacted = dict(row)
    redacted["cwd"] = str(redacted.get("cwd", "")).replace(needle, replacement)
    redacted["commands"] = [
        str(command).replace(needle, replacement)
        for command in redacted.get("commands", [])
    ]
    return redacted


def _command_name(command: str) -> str:
    parts = command.strip().split()
    if not parts:
        return ""
    first = Path(parts[0].strip("\"'")).name
    if first == "sudo" and len(parts) > 1:
        return Path(parts[1].strip("\"'")).name
    return first


def _topic_for(commands: Sequence[str]) -> str:
    for command in commands:
        topic = TOOL_TOPICS.get(_command_name(command).lower())
        if topic:
            return topic
    return "personal"


def _usable_candidate(row: dict) -> bool:
    commands = [str(command) for command in row.get("commands", [])]
    if len(commands) < 2:
        return False
    if likely_secret("\n".join([str(row.get("cwd", "")), *commands])):
        return False
    useful = [
        command for command in commands
        if _command_name(command).lower() not in NOISE_COMMANDS
    ]
    return len(useful) >= 2


def _bootstrap_queries(row: dict, topic: str, q_start: int) -> list[dict]:
    sid = row["session_id"]
    cwd = Path(str(row.get("cwd") or "work")).name or "work"
    tools = []
    for command in row.get("commands", []):
        tool = _command_name(command).lower()
        if tool and tool not in NOISE_COMMANDS and tool not in tools:
            tools.append(tool)
    tool_text = ", ".join(tools[:3]) if tools else "commands"
    return [
        {
            "query_id": f"personal_q{q_start:06d}",
            "query": f"the {topic} work I did in {cwd} using {tool_text}",
            "correct_session_id": sid,
            "topic": topic,
            "kind": "intent",
            "priority": "bootstrap",
            "generated": True,
        },
        {
            "query_id": f"personal_q{q_start + 1:06d}",
            "query": f"where I was working through a {topic} task from that {cwd} session",
            "correct_session_id": sid,
            "topic": topic,
            "kind": "intent",
            "priority": "bootstrap",
            "generated": True,
        },
    ]


def bootstrap_personal(
    candidates: Path,
    out_dir: Path,
    *,
    sessions_target: int = 50,
    null_target: int = 15,
    allow_unsafe_path: bool = False,
) -> tuple[int, int]:
    """Create a generated private draft suite from exported candidates.

    Bootstrap labels are useful for exercising the pipeline, but human-authored
    labels remain the promotion gate.
    """
    if not allow_unsafe_path:
        _ensure_private_path(out_dir)
    init_personal(out_dir)
    paths = personal_paths(out_dir)
    existing_sessions = {row["session_id"] for row in _read_existing(paths["sessions"])}
    existing_queries = _read_existing(paths["queries"])
    next_q = _next_query_index(existing_queries)
    selected: list[dict] = []
    queries: list[dict] = []
    topic_counts: dict[str, int] = {}

    for row in load_jsonl(candidates):
        if row["session_id"] in existing_sessions or not _usable_candidate(row):
            continue
        topic = _topic_for(row.get("commands", []))
        if topic_counts.get(topic, 0) >= 8:
            continue
        row = dict(row)
        row["topic"] = topic
        row["bootstrap"] = True
        selected.append(row)
        queries.extend(_bootstrap_queries(row, topic, next_q))
        next_q += 2
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
        if len(selected) >= sessions_target:
            break

    null_templates = [
        ("terraform cloud infrastructure provisioning", "terraform-null"),
        ("kubernetes secret rotation in a namespace", "kubernetes-null"),
        ("postgres slow query explain analyze index tuning", "postgres-null"),
        ("nginx rate limiting burst configuration", "nginx-null"),
        ("github actions workflow cache failure", "ci-null"),
        ("rust borrow checker lifetime error", "rust-null"),
        ("redis pub sub channel debugging", "redis-null"),
        ("aws iam access key rotation", "aws-null"),
        ("bluetooth audio pairing configuration", "bluetooth-null"),
        ("oauth callback redirect mismatch", "oauth-null"),
        ("elasticsearch shard allocation tuning", "search-null"),
        ("helm chart values rollback", "helm-null"),
        ("mysql replication lag troubleshooting", "mysql-null"),
        ("cuda driver gpu training failure", "gpu-null"),
        ("ansible playbook inventory variable issue", "ansible-null"),
    ]
    for text, topic in null_templates[:null_target]:
        queries.append(
            {
                "query_id": f"personal_q{next_q:06d}",
                "query": text,
                "correct_session_id": None,
                "topic": topic,
                "kind": "null",
                "priority": "bootstrap",
                "generated": True,
            }
        )
        next_q += 1

    final_sessions = [*_read_existing(paths["sessions"]), *selected]
    final_queries = [*_read_existing(paths["queries"]), *queries]
    _validate_personal_rows(final_sessions, final_queries)
    _append_jsonl(paths["sessions"], selected)
    _append_jsonl(paths["queries"], queries)
    print(f"bootstrapped {len(selected)} sessions and {len(queries)} queries")
    return len(selected), len(queries)


def _print_candidate(row: dict) -> None:
    print("\n" + "=" * 72)
    print(f"{row['session_id']}  cwd={row.get('cwd', '?')}")
    for i, cmd in enumerate(row.get("commands", []), start=1):
        print(f"{i:>2}: {cmd}")


def label_candidates(candidates: Path, out_dir: Path, *, allow_unsafe_path: bool = False) -> None:
    """Minimal interactive labeler for private local use."""
    if not allow_unsafe_path:
        _ensure_private_path(out_dir)
    init_personal(out_dir)
    rows = load_jsonl(candidates)
    paths = personal_paths(out_dir)
    sessions_to_add: list[dict] = []
    queries_to_add: list[dict] = []
    existing_sessions = {row["session_id"] for row in _read_existing(paths["sessions"])}
    existing_queries = _read_existing(paths["queries"])
    next_q = _next_query_index(existing_queries)

    for row in rows:
        if row["session_id"] in existing_sessions:
            continue
        while True:
            _print_candidate(row)
            action = input("action [s=save, r=redact, x=skip, q=quit] ").strip().lower()
            if action == "r":
                needle = input("text to redact: ")
                replacement = input("replacement [[REDACTED]]: ").strip() or "[REDACTED]"
                if needle:
                    row = _redact_row(row, needle, replacement)
                continue
            break
        if action == "q":
            break
        if action != "s":
            continue
        topic = input("topic: ").strip() or row.get("topic") or "personal"
        row["topic"] = topic
        sessions_to_add.append(row)
        existing_sessions.add(row["session_id"])
        while True:
            kind = input("query kind [i=intent,e=error,f=fragment,n=null,enter=done]: ").strip().lower()
            if not kind:
                break
            if kind not in {"i", "e", "f", "n"}:
                print("unknown kind")
                continue
            query_text = input("query: ").strip()
            if not query_text:
                continue
            kind_name = {"i": "intent", "e": "error", "f": "fragment", "n": "null"}[kind]
            queries_to_add.append(
                {
                    "query_id": f"personal_q{next_q:06d}",
                    "query": query_text,
                    "correct_session_id": None if kind_name == "null" else row["session_id"],
                    "topic": topic if kind_name != "null" else f"{topic}-null",
                    "kind": kind_name,
                    "priority": "promotion",
                }
            )
            next_q += 1

    existing_session_rows = _read_existing(paths["sessions"])
    existing_query_rows = _read_existing(paths["queries"])
    _validate_personal_rows(
        [*existing_session_rows, *sessions_to_add],
        [*existing_query_rows, *queries_to_add],
    )
    _append_jsonl(paths["sessions"], sessions_to_add)
    _append_jsonl(paths["queries"], queries_to_add)
    validate_personal(out_dir)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("--dir", type=Path, default=DEFAULT_DIR)

    export = sub.add_parser("export")
    export.add_argument("--db", type=Path, default=Config.default().db_path)
    export.add_argument("--out", type=Path, default=personal_paths()["candidates"])
    export.add_argument("--limit", type=int, default=300)

    label = sub.add_parser("label")
    label.add_argument("--candidates", type=Path, default=personal_paths()["candidates"])
    label.add_argument("--out-dir", type=Path, default=DEFAULT_DIR)

    validate = sub.add_parser("validate")
    validate.add_argument("dir", nargs="?", type=Path, default=DEFAULT_DIR)
    validate.add_argument("--strict-size", action="store_true")

    status = sub.add_parser("status")
    status.add_argument("dir", nargs="?", type=Path, default=DEFAULT_DIR)

    bootstrap = sub.add_parser("bootstrap")
    bootstrap.add_argument("--candidates", type=Path, default=personal_paths()["candidates"])
    bootstrap.add_argument("--out-dir", type=Path, default=DEFAULT_DIR)
    bootstrap.add_argument("--sessions", type=int, default=50)
    bootstrap.add_argument("--nulls", type=int, default=15)

    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "init":
        init_personal(args.dir)
    elif args.command == "export":
        export_candidates(args.db, args.out, limit=args.limit)
    elif args.command == "label":
        label_candidates(args.candidates, args.out_dir)
    elif args.command == "validate":
        validate_personal(args.dir, strict_size=args.strict_size)
    elif args.command == "status":
        status_personal(args.dir)
    elif args.command == "bootstrap":
        bootstrap_personal(
            args.candidates,
            args.out_dir,
            sessions_target=args.sessions,
            null_target=args.nulls,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
