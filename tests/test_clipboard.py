"""Tests for clipboard and text truncation helpers."""

from __future__ import annotations

from unittest.mock import patch

from whatwasit.clipboard import copy_to_clipboard
from whatwasit.textutil import truncate_display, truncate_for_embed


def test_truncate_display_adds_ellipsis() -> None:
    text = "x" * 120
    out = truncate_display(text, max_chars=40)
    assert len(out) == 40
    assert out.endswith("…")


def test_truncate_for_embed_caps_length() -> None:
    text = "y" * 1000
    assert len(truncate_for_embed(text, max_chars=512)) == 512


def test_copy_to_clipboard_uses_available_tool() -> None:
    with patch("whatwasit.clipboard.shutil.which", return_value="/usr/bin/wl-copy"):
        with patch("whatwasit.clipboard.subprocess.run") as run:
            run.return_value.returncode = 0
            assert copy_to_clipboard("hello") is True
            run.assert_called_once()
