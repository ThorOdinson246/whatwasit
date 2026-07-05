from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "eval"
TOKEN_RE = re.compile(r"[a-z0-9_.:/-]+")

ALLOWED_INTENT_OVERLAP = {
    "api",
    "branch",
    "config",
    "container",
    "database",
    "dev",
    "file",
    "files",
    "host",
    "local",
    "login",
    "machine",
    "package",
    "process",
    "project",
    "proxy",
    "remote",
    "script",
    "server",
    "tests",
}


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def test_hard_suite_schema_and_gold_ids() -> None:
    sessions = _load_jsonl(EVAL_DIR / "hard_sessions.jsonl")
    queries = _load_jsonl(EVAL_DIR / "hard_queries.jsonl")

    session_ids = [row["session_id"] for row in sessions]
    query_ids = [row["query_id"] for row in queries]

    assert len(session_ids) == len(set(session_ids))
    assert len(query_ids) == len(set(query_ids))
    assert {row["kind"] for row in queries} == {"intent", "error", "fragment", "null"}

    known = set(session_ids)
    answerable = [row for row in queries if row["correct_session_id"] is not None]
    nulls = [row for row in queries if row["correct_session_id"] is None]

    assert len(sessions) >= 18
    assert len(answerable) >= 24
    assert len(nulls) >= 5
    assert all(row["correct_session_id"] in known for row in answerable)
    assert all(row["kind"] == "null" for row in nulls)


def test_hard_suite_has_confusable_clusters() -> None:
    sessions = _load_jsonl(EVAL_DIR / "hard_sessions.jsonl")
    by_topic: dict[str, int] = {}
    for row in sessions:
        by_topic[row["topic"]] = by_topic.get(row["topic"], 0) + 1

    assert by_topic["git-conflicts"] >= 2
    assert by_topic["docker-storage"] >= 2
    assert by_topic["dns"] >= 2
    assert by_topic["nginx"] >= 2
    assert by_topic["db-migrations"] >= 2
    assert by_topic["python"] >= 2


def test_intent_queries_avoid_specific_command_leakage() -> None:
    sessions = {
        row["session_id"]: row for row in _load_jsonl(EVAL_DIR / "hard_sessions.jsonl")
    }
    queries = _load_jsonl(EVAL_DIR / "hard_queries.jsonl")

    for query in queries:
        if query["kind"] != "intent":
            continue
        session = sessions[query["correct_session_id"]]
        command_text = " ".join(session["commands"]).lower()
        command_tokens = {
            token
            for token in TOKEN_RE.findall(command_text)
            if len(token) >= 5 and token not in ALLOWED_INTENT_OVERLAP
        }
        query_tokens = set(TOKEN_RE.findall(query["query"].lower()))
        leaked = sorted(command_tokens & query_tokens)
        assert leaked == [], f"{query['query_id']} leaks {leaked}"
