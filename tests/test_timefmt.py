"""Tests for whatwasit.timefmt."""

from __future__ import annotations

from datetime import datetime

from whatwasit.timefmt import format_relative_time, format_timestamp


def test_format_timestamp_none() -> None:
    assert format_timestamp(None) == "unknown"


def test_format_relative_time_buckets() -> None:
    now = datetime(2026, 7, 2, 18, 0, 0)
    assert format_relative_time(int(now.timestamp()), now=now) == "just now"
    assert format_relative_time(int(now.timestamp()) - 120, now=now) == "2m ago"
    assert format_relative_time(int(now.timestamp()) - 7200, now=now) == "2h ago"
    assert format_relative_time(int(now.timestamp()) - 86400, now=now) == "1d ago"
