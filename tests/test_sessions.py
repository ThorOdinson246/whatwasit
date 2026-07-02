"""Tests for whatwasit.sessions: cwd reconstruction and session grouping."""

from __future__ import annotations

from whatwasit.config import Config
from whatwasit.models import Command
from whatwasit.sessions import group_commands, reconstruct_cwd


def make_cmd(raw_cmd, ts=None, cwd=None, source="zsh"):
    return Command(raw_cmd=raw_cmd, ts=ts, source=source, cwd=cwd)


# --------------------------------------------------------------------------
# reconstruct_cwd
# --------------------------------------------------------------------------


def test_reconstruct_cwd_absolute_cd():
    commands = [
        make_cmd("ls"),
        make_cmd("cd /var/log"),
        make_cmd("tail nginx/error.log"),
    ]
    reconstruct_cwd(commands, start_cwd="~")

    assert commands[0].cwd == "~"
    assert commands[1].cwd == "/var/log"  # cd attributed to its destination
    assert commands[2].cwd == "/var/log"


def test_reconstruct_cwd_relative_cd():
    commands = [
        make_cmd("cd /home/user/project"),
        make_cmd("cd src"),
        make_cmd("ls"),
        make_cmd("cd ../tests"),
        make_cmd("pytest"),
    ]
    reconstruct_cwd(commands, start_cwd="~")

    assert commands[0].cwd == "/home/user/project"
    assert commands[1].cwd == "/home/user/project/src"
    assert commands[2].cwd == "/home/user/project/src"
    assert commands[3].cwd == "/home/user/project/tests"
    assert commands[4].cwd == "/home/user/project/tests"


def test_reconstruct_cwd_home_relative_no_double_tilde():
    commands = [make_cmd("cd ~/Downloads"), make_cmd("ls")]
    reconstruct_cwd(commands, start_cwd="~")

    assert commands[0].cwd == "~/Downloads"
    assert commands[1].cwd == "~/Downloads"


def test_reconstruct_cwd_cd_ignores_trailing_tokens():
    # History can carry multi-token/backslash-joined entries; cd must only
    # consume its first argument, not let later tokens leak into the path.
    commands = [make_cmd("cd ~/Downloads wget https://example.com/x")]
    reconstruct_cwd(commands, start_cwd="~")

    assert commands[0].cwd == "~/Downloads"


def test_reconstruct_cwd_cd_dash_swaps_oldpwd():
    commands = [
        make_cmd("cd /a"),
        make_cmd("cd /b"),
        make_cmd("cd -"),
        make_cmd("pwd"),
        make_cmd("cd -"),
        make_cmd("pwd"),
    ]
    reconstruct_cwd(commands, start_cwd="~")

    # after "cd /a" -> /a, after "cd /b" -> /b
    # "cd -" runs while in /b, taking us back to /a (oldpwd)
    assert commands[3].cwd == "/a"
    # next "cd -" swaps again, back to /b
    assert commands[5].cwd == "/b"


def test_reconstruct_cwd_pushd_popd():
    commands = [
        make_cmd("cd /a"),
        make_cmd("pushd /b"),
        make_cmd("pwd"),  # should be in /b
        make_cmd("popd"),
        make_cmd("pwd"),  # back to /a
    ]
    reconstruct_cwd(commands, start_cwd="~")

    assert commands[2].cwd == "/b"
    assert commands[4].cwd == "/a"


def test_reconstruct_cwd_unresolvable_keeps_prior_dir():
    commands = [
        make_cmd("cd /a"),
        make_cmd("cd $PROJECT_DIR"),
        make_cmd("pwd"),
    ]
    reconstruct_cwd(commands, start_cwd="~")

    # The cd to $PROJECT_DIR can't be resolved statically, so we stay in /a.
    assert commands[1].cwd == "/a"
    assert commands[2].cwd == "/a"


def test_reconstruct_cwd_does_not_overwrite_existing_cwd():
    commands = [
        make_cmd("cd /a"),
        make_cmd("cd /b", cwd="/already/known"),
        make_cmd("pwd"),
    ]
    reconstruct_cwd(commands, start_cwd="~")

    # Pre-set cwd (e.g. from atuin) must never be overwritten.
    assert commands[1].cwd == "/already/known"
    # But the tracked state still resyncs from it and replays the cd /b
    # for subsequent commands.
    assert commands[2].cwd == "/b"


# --------------------------------------------------------------------------
# group_commands
# --------------------------------------------------------------------------


def test_group_commands_splits_on_time_gap():
    config = Config(session_window_seconds=300, split_on_cwd_change=False)
    commands = [
        make_cmd("ls", ts=1000, cwd="/proj"),
        make_cmd("pwd", ts=1100, cwd="/proj"),
        # gap of 400s > 300s window
        make_cmd("git status", ts=1500, cwd="/proj"),
    ]
    sessions = group_commands(commands, config)

    assert len(sessions) == 2
    assert sessions[0].commands == commands[:2]
    assert sessions[1].commands == commands[2:]


def test_group_commands_no_split_within_window():
    config = Config(session_window_seconds=300, split_on_cwd_change=False)
    commands = [
        make_cmd("ls", ts=1000, cwd="/proj"),
        make_cmd("pwd", ts=1200, cwd="/proj"),
        make_cmd("git status", ts=1290, cwd="/proj"),
    ]
    sessions = group_commands(commands, config)

    assert len(sessions) == 1
    assert sessions[0].commands == commands


def test_group_commands_splits_on_cwd_change():
    config = Config(session_window_seconds=300, split_on_cwd_change=True)
    commands = [
        make_cmd("ls", ts=1000, cwd="/proj-a"),
        make_cmd("pwd", ts=1010, cwd="/proj-a"),
        make_cmd("git status", ts=1020, cwd="/proj-b"),
    ]
    sessions = group_commands(commands, config)

    assert len(sessions) == 2
    assert sessions[0].cwd == "/proj-a"
    assert sessions[1].cwd == "/proj-b"


def test_group_commands_cwd_change_ignored_when_disabled():
    config = Config(session_window_seconds=300, split_on_cwd_change=False)
    commands = [
        make_cmd("ls", ts=1000, cwd="/proj-a"),
        make_cmd("git status", ts=1010, cwd="/proj-b"),
    ]
    sessions = group_commands(commands, config)

    assert len(sessions) == 1


def test_group_commands_no_timestamps_splits_on_cwd_only():
    config = Config(session_window_seconds=300, split_on_cwd_change=True)
    commands = [
        make_cmd("ls", cwd="/proj-a"),
        make_cmd("pwd", cwd="/proj-a"),
        make_cmd("git status", cwd="/proj-b"),
        make_cmd("git log", cwd="/proj-b"),
    ]
    sessions = group_commands(commands, config)

    assert len(sessions) == 2
    assert [c.raw_cmd for c in sessions[0].commands] == ["ls", "pwd"]
    assert [c.raw_cmd for c in sessions[1].commands] == ["git status", "git log"]


def test_group_commands_no_timestamps_no_cwd_change_single_session():
    config = Config(session_window_seconds=300, split_on_cwd_change=True)
    commands = [
        make_cmd("ls", cwd="/proj"),
        make_cmd("pwd", cwd="/proj"),
        make_cmd("git status", cwd="/proj"),
    ]
    sessions = group_commands(commands, config)

    assert len(sessions) == 1


def test_group_commands_session_start_end_ts_and_cwd():
    config = Config(session_window_seconds=300, split_on_cwd_change=True)
    commands = [
        make_cmd("ls", ts=2000, cwd="/proj"),
        make_cmd("pwd", ts=2050, cwd="/proj"),
        make_cmd("vim main.py", ts=2100, cwd="/proj"),
    ]
    sessions = group_commands(commands, config)

    assert len(sessions) == 1
    session = sessions[0]
    assert session.start_ts == 2000
    assert session.end_ts == 2100
    assert session.cwd == "/proj"
    assert session.command_count == 3


def test_group_commands_session_ts_none_when_all_missing():
    config = Config(session_window_seconds=300, split_on_cwd_change=True)
    commands = [
        make_cmd("ls", cwd="/proj"),
        make_cmd("pwd", cwd="/proj"),
    ]
    sessions = group_commands(commands, config)

    assert len(sessions) == 1
    assert sessions[0].start_ts is None
    assert sessions[0].end_ts is None


def test_group_commands_doc_text_is_populated():
    config = Config(session_window_seconds=300, split_on_cwd_change=True)
    commands = [
        make_cmd("ls -la", ts=1000, cwd="/home/user/myproject"),
        make_cmd("git status", ts=1010, cwd="/home/user/myproject"),
    ]
    sessions = group_commands(commands, config)

    assert len(sessions) == 1
    doc_text = sessions[0].doc_text
    assert doc_text
    assert "myproject" in doc_text
    assert "ls -la" in doc_text
    assert "git status" in doc_text


def test_group_commands_reconstructs_missing_cwd_first():
    config = Config(session_window_seconds=300, split_on_cwd_change=True)
    commands = [
        make_cmd("cd /work"),
        make_cmd("ls"),
        make_cmd("cd /other"),
        make_cmd("pwd"),
    ]
    sessions = group_commands(commands, config)

    # cwd is reconstructed in place before grouping; a "cd" is attributed to
    # its destination, so "cd /work" and the following "ls" share the /work
    # session, and "cd /other" starts the next one.
    assert commands[0].cwd == "/work"
    assert commands[1].cwd == "/work"
    assert commands[2].cwd == "/other"
    assert commands[3].cwd == "/other"
    assert len(sessions) == 2
    assert sessions[0].cwd == "/work"
    assert [c.raw_cmd for c in sessions[0].commands] == ["cd /work", "ls"]
    assert sessions[1].cwd == "/other"
    assert [c.raw_cmd for c in sessions[1].commands] == ["cd /other", "pwd"]


def test_group_commands_preserves_original_order():
    config = Config(session_window_seconds=300, split_on_cwd_change=False)
    commands = [
        make_cmd("a", ts=1, cwd="/x"),
        make_cmd("b", ts=2, cwd="/x"),
        make_cmd("c", ts=3, cwd="/x"),
    ]
    sessions = group_commands(commands, config)

    assert len(sessions) == 1
    assert [c.raw_cmd for c in sessions[0].commands] == ["a", "b", "c"]
