from __future__ import annotations

import json

import pytest

from eval.personal import (
    export_candidates,
    init_personal,
    likely_secret,
    personal_paths,
    validate_personal,
)
from whatwasit import db
from whatwasit.models import Command, Session


def _jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def test_init_personal_creates_private_layout(tmp_path) -> None:
    root = tmp_path / "personal"
    init_personal(root)
    paths = personal_paths(root)

    assert paths["sessions"].is_file()
    assert paths["queries"].is_file()
    assert paths["baselines"].is_dir()
    assert paths["runs"].is_dir()


def test_export_candidates_from_whatwasit_db(tmp_path) -> None:
    db_path = tmp_path / "whatwasit.db"
    conn = db.connect(db_path)
    db.initialize(conn)
    session = Session(
        cwd="~/project",
        commands=[
            Command(raw_cmd="python -m pytest", source="zsh"),
            Command(raw_cmd="git status", source="zsh"),
        ],
    )
    db.insert_session(conn, session)
    conn.commit()
    conn.close()

    out = tmp_path / "candidates.jsonl"
    export_candidates(db_path, out, limit=10)

    rows = _jsonl(out)
    assert rows[0]["session_id"] == "personal_000000"
    assert rows[0]["commands"] == ["python -m pytest", "git status"]
    assert rows[0]["provenance"]["private"] is True


def test_validate_personal_rejects_secret_like_sessions(tmp_path) -> None:
    root = tmp_path / "personal"
    init_personal(root)
    paths = personal_paths(root)
    paths["sessions"].write_text(
        json.dumps(
            {
                "session_id": "s1",
                "topic": "secret",
                "cwd": "~",
                "commands": ["curl -H 'Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456'"],
            }
        )
        + "\n"
    )

    with pytest.raises(SystemExit, match="likely secret"):
        validate_personal(root)


def test_validate_personal_accepts_valid_private_suite(tmp_path) -> None:
    root = tmp_path / "personal"
    init_personal(root)
    paths = personal_paths(root)
    paths["sessions"].write_text(
        json.dumps(
            {
                "session_id": "s1",
                "topic": "docker",
                "cwd": "~",
                "commands": ["docker compose up -d"],
            }
        )
        + "\n"
    )
    paths["queries"].write_text(
        json.dumps(
            {
                "query_id": "q1",
                "query": "bringing up my local stack",
                "correct_session_id": "s1",
                "topic": "docker",
                "kind": "intent",
            }
        )
        + "\n"
    )

    assert validate_personal(root) == (1, 1)


def test_likely_secret_patterns() -> None:
    assert likely_secret("AWS_SECRET_ACCESS_KEY=abc")
    assert likely_secret("Authorization: Bearer abcdefghijklmnopqrstuvwxyz")
    assert not likely_secret("docker compose up -d")
