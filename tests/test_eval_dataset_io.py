from __future__ import annotations

import pytest

from eval.dataset_io import (
    dataset_stats,
    load_raw_commands,
    normalize_raw_command,
    raw_commands_to_sessions,
    validate_queries,
    validate_sessions,
)


def test_validate_sessions_and_queries() -> None:
    sessions = [
        {
            "session_id": "s1",
            "topic": "topic",
            "cwd": "~",
            "commands": ["echo hello"],
        }
    ]
    queries = [
        {"query_id": "q1", "query": "say hello", "correct_session_id": "s1", "topic": "topic"},
        {"query_id": "q2", "query": "missing thing", "correct_session_id": None, "topic": "null"},
    ]

    validate_sessions(sessions)
    validate_queries(queries, {"s1"})
    assert dataset_stats(sessions, queries).answerable == 1
    assert dataset_stats(sessions, queries).null == 1


def test_validate_queries_rejects_unknown_gold() -> None:
    with pytest.raises(ValueError, match="unknown correct_session_id"):
        validate_queries(
            [{"query_id": "q", "query": "x", "correct_session_id": "missing", "topic": "t"}],
            {"known"},
        )


def test_normalize_raw_command_filters_noise() -> None:
    assert normalize_raw_command("$ docker ps") == "docker ps"
    assert normalize_raw_command("  % git status") == "git status"
    assert normalize_raw_command("# comment") is None
    assert normalize_raw_command("exit") is None


def test_raw_command_loading_and_grouping_is_deterministic(tmp_path) -> None:
    raw = tmp_path / "commands.txt"
    raw.write_text("$ docker ps\nclear\n$ docker ps\npytest -q\nls -la\ncurl localhost\n")

    commands = load_raw_commands([raw])
    assert commands == ["docker ps", "pytest -q", "ls -la", "curl localhost"]

    sessions = raw_commands_to_sessions(
        commands,
        suite="raw_noise",
        source="fixture",
        session_size=2,
    )
    assert [row["session_id"] for row in sessions] == ["raw_noise_0000", "raw_noise_0001"]
    assert sessions[0]["commands"] == ["docker ps", "pytest -q"]
    assert sessions[0]["provenance"]["source"] == "fixture"
