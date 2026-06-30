"""Tests for the zsh/bash/atuin history parsers."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from hist.parsers.atuin import parse_atuin
from hist.parsers.bash import parse_bash
from hist.parsers.zsh import parse_zsh


# --------------------------------------------------------------------------
# zsh
# --------------------------------------------------------------------------


def test_zsh_extended_history(tmp_path: Path) -> None:
    hist_file = tmp_path / ".zsh_history"
    hist_file.write_text(
        ": 1700000000:5;echo hello\n"
        ": 1700000100:0;ls -la\n"
    )

    commands = parse_zsh(hist_file)

    assert len(commands) == 2
    assert commands[0].raw_cmd == "echo hello"
    assert commands[0].ts == 1700000000
    assert commands[0].duration == 5
    assert commands[0].source == "zsh"

    assert commands[1].raw_cmd == "ls -la"
    assert commands[1].ts == 1700000100
    assert commands[1].duration == 0


def test_zsh_plain_lines(tmp_path: Path) -> None:
    hist_file = tmp_path / ".zsh_history"
    hist_file.write_text("echo plain\npwd\n")

    commands = parse_zsh(hist_file)

    assert len(commands) == 2
    assert commands[0].raw_cmd == "echo plain"
    assert commands[0].ts is None
    assert commands[0].duration is None
    assert commands[0].source == "zsh"
    assert commands[1].raw_cmd == "pwd"
    assert commands[1].ts is None


def test_zsh_multiline_backslash_join(tmp_path: Path) -> None:
    hist_file = tmp_path / ".zsh_history"
    hist_file.write_text(
        ": 1700000200:2;echo foo \\\nbar \\\nbaz\n"
        "pwd\n"
    )

    commands = parse_zsh(hist_file)

    assert len(commands) == 2
    assert commands[0].raw_cmd == "echo foo \nbar \nbaz"
    assert commands[0].ts == 1700000200
    assert commands[0].duration == 2
    assert commands[1].raw_cmd == "pwd"


def test_zsh_skips_malformed_lines(tmp_path: Path) -> None:
    hist_file = tmp_path / ".zsh_history"
    hist_file.write_text(
        "\n"
        ": notanumber:5;broken prefix\n"
        "echo ok\n"
    )

    commands = parse_zsh(hist_file)

    # Blank line skipped; malformed extended-history prefix falls back to a
    # plain command line rather than crashing.
    raw_cmds = [c.raw_cmd for c in commands]
    assert "echo ok" in raw_cmds
    assert any("broken prefix" in c for c in raw_cmds)


def test_zsh_missing_file_returns_empty(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist"
    assert parse_zsh(missing) == []


# --------------------------------------------------------------------------
# bash
# --------------------------------------------------------------------------


def test_bash_with_epoch_timestamps(tmp_path: Path) -> None:
    hist_file = tmp_path / ".bash_history"
    hist_file.write_text(
        "#1700000300\n"
        "echo timed\n"
        "#1700000400\n"
        "ls\n"
    )

    commands = parse_bash(hist_file)

    assert len(commands) == 2
    assert commands[0].raw_cmd == "echo timed"
    assert commands[0].ts == 1700000300
    assert commands[0].source == "bash"
    assert commands[1].raw_cmd == "ls"
    assert commands[1].ts == 1700000400


def test_bash_without_timestamps(tmp_path: Path) -> None:
    hist_file = tmp_path / ".bash_history"
    hist_file.write_text("echo untimed\npwd\n")

    commands = parse_bash(hist_file)

    assert len(commands) == 2
    assert commands[0].raw_cmd == "echo untimed"
    assert commands[0].ts is None
    assert commands[0].source == "bash"
    assert commands[1].raw_cmd == "pwd"
    assert commands[1].ts is None


def test_bash_mixed_timestamps(tmp_path: Path) -> None:
    hist_file = tmp_path / ".bash_history"
    hist_file.write_text(
        "echo notimestamp\n"
        "#1700000500\n"
        "echo withtimestamp\n"
    )

    commands = parse_bash(hist_file)

    assert len(commands) == 2
    assert commands[0].raw_cmd == "echo notimestamp"
    assert commands[0].ts is None
    assert commands[1].raw_cmd == "echo withtimestamp"
    assert commands[1].ts == 1700000500


def test_bash_missing_file_returns_empty(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist"
    assert parse_bash(missing) == []


# --------------------------------------------------------------------------
# atuin
# --------------------------------------------------------------------------


def _make_atuin_db(path: Path, rows, columns) -> None:
    conn = sqlite3.connect(str(path))
    try:
        col_defs = ", ".join(f"{c} TEXT" if c == "command" or c == "cwd" else f"{c} INTEGER" for c in columns)
        conn.execute(f"CREATE TABLE history (id INTEGER PRIMARY KEY, {col_defs})")
        placeholders = ", ".join("?" for _ in columns)
        conn.executemany(
            f"INSERT INTO history ({', '.join(columns)}) VALUES ({placeholders})",
            rows,
        )
        conn.commit()
    finally:
        conn.close()


def test_atuin_parses_nanosecond_timestamp_and_cwd(tmp_path: Path) -> None:
    db_path = tmp_path / "history.db"
    columns = ["timestamp", "duration", "exit", "command", "cwd"]
    rows = [
        (1700000600_000000000, 3, 0, "echo atuin", "/home/user/project"),
        (1700000700_000000000, 0, 1, "false", "/tmp"),
    ]
    _make_atuin_db(db_path, rows, columns)

    commands = parse_atuin(db_path)

    assert len(commands) == 2
    first = commands[0]
    assert first.raw_cmd == "echo atuin"
    assert first.ts == 1700000600
    assert first.duration == 3
    assert first.exit_code == 0
    assert first.cwd == "/home/user/project"
    assert first.source == "atuin"

    second = commands[1]
    assert second.raw_cmd == "false"
    assert second.ts == 1700000700
    assert second.exit_code == 1
    assert second.cwd == "/tmp"


def test_atuin_tolerates_missing_columns(tmp_path: Path) -> None:
    db_path = tmp_path / "history.db"
    # Only "command" is present; everything else is missing from the schema.
    columns = ["command"]
    rows = [("just a command",)]
    _make_atuin_db(db_path, rows, columns)

    commands = parse_atuin(db_path)

    assert len(commands) == 1
    assert commands[0].raw_cmd == "just a command"
    assert commands[0].ts is None
    assert commands[0].duration is None
    assert commands[0].exit_code is None
    assert commands[0].cwd is None
    assert commands[0].source == "atuin"


def test_atuin_missing_db_returns_empty(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.db"
    assert parse_atuin(missing) == []


def test_atuin_does_not_mutate_source_db(tmp_path: Path) -> None:
    db_path = tmp_path / "history.db"
    columns = ["timestamp", "command"]
    rows = [(1700000800_000000000, "echo readonly")]
    _make_atuin_db(db_path, rows, columns)

    before = db_path.read_bytes()
    parse_atuin(db_path)
    after = db_path.read_bytes()

    assert before == after
