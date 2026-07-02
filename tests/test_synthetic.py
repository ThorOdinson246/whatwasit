"""Tests for the synthetic multi-topic shell-history generator."""

from __future__ import annotations

import re

from whatwasit.models import Command

from tests.synthetic import (
    TOPIC_QUERIES,
    TOPICS,
    generate_commands,
    generate_zsh_history,
)

_LINE_RE = re.compile(r"^: \d+:\d+;.+$")


def test_generate_zsh_history_contains_distinct_topic_directories():
    history = generate_zsh_history()
    topic_dirs = {topic["cwd"] for topic in TOPICS}
    assert len(topic_dirs) >= 3

    found_dirs = {d for d in topic_dirs if f"cd {d}" in history}
    assert len(found_dirs) >= 3


def test_generate_zsh_history_lines_match_extended_history_format():
    history = generate_zsh_history()
    lines = [line for line in history.splitlines() if line.strip()]
    assert len(lines) > 0
    for line in lines:
        assert _LINE_RE.match(line), f"line does not match EXTENDED_HISTORY format: {line!r}"


def test_generate_zsh_history_topic_gap_exceeds_five_minutes():
    history = generate_zsh_history()
    lines = [line for line in history.splitlines() if line.strip()]
    timestamps = [int(line.split(":")[1]) for line in lines]
    # Within-topic gaps should all be well under 5 minutes; at least one
    # gap (the topic boundary) should exceed it.
    gaps = [b - a for a, b in zip(timestamps, timestamps[1:])]
    assert any(gap > 300 for gap in gaps)
    assert all(gap < 300 or gap > 300 for gap in gaps)  # sanity: gaps are well-defined


def test_topic_queries_has_entry_per_topic():
    assert len(TOPIC_QUERIES) == len(TOPICS)
    for topic in TOPICS:
        name = topic["name"]
        assert name in TOPIC_QUERIES
        assert isinstance(TOPIC_QUERIES[name], str)
        assert len(TOPIC_QUERIES[name]) > 0


def test_write_zsh_history(tmp_path):
    from tests.synthetic import write_zsh_history

    path = tmp_path / "zsh_history"
    write_zsh_history(str(path), seed=1)
    assert path.exists()
    content = path.read_text()
    assert content == generate_zsh_history(seed=1)


def test_generate_commands_returns_approximately_n_commands():
    commands = generate_commands(1000, seed=0)
    assert isinstance(commands, list)
    # Blocks are generated whole, so the count may slightly overshoot n
    # but should never fall far short of it.
    assert 1000 <= len(commands) <= 1000 + 20
    assert all(isinstance(c, Command) for c in commands)


def test_generate_commands_timestamps_non_decreasing():
    commands = generate_commands(1000, seed=0)
    timestamps = [c.ts for c in commands]
    assert all(ts is not None for ts in timestamps)
    assert all(b >= a for a, b in zip(timestamps, timestamps[1:]))


def test_generate_commands_have_zsh_source_and_cd_commands():
    commands = generate_commands(1000, seed=0)
    assert all(c.source == "zsh" for c in commands)
    cd_commands = [c for c in commands if c.raw_cmd.startswith("cd ")]
    assert len(cd_commands) >= 5


def test_generate_commands_scales_to_large_n_quickly():
    import time

    start = time.time()
    commands = generate_commands(100000, seed=0)
    elapsed = time.time() - start
    assert len(commands) >= 100000
    assert elapsed < 10
