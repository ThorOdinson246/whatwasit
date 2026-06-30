"""Core data models shared across every module.

These dataclasses are the frozen contract between the parser, grouper, indexer,
search, and output layers. Changing their public shape is a cross-module change.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional

UNKNOWN_CWD = "?"
"""Sentinel for a working directory that could not be reconstructed."""


@dataclass
class Command:
    """A single command read from a shell history source.

    Attributes:
        raw_cmd: The exact command text as recorded.
        ts: Unix epoch seconds, or ``None`` if the source has no timestamps
            (e.g. bash without ``HISTTIMEFORMAT``).
        source: Origin of the record, e.g. ``"zsh"``, ``"bash"``, ``"atuin"``.
        cwd: Working directory. ``None`` if unknown before reconstruction.
        duration: Command duration in seconds/ms if known, else ``None``.
        exit_code: Process exit code if known, else ``None``.
    """

    raw_cmd: str
    ts: Optional[int] = None
    source: str = "unknown"
    cwd: Optional[str] = None
    duration: Optional[int] = None
    exit_code: Optional[int] = None


@dataclass
class Session:
    """A contiguous group of commands the user ran while doing one thing.

    ``id`` is ``None`` until the session is persisted to SQLite.
    """

    commands: List[Command] = field(default_factory=list)
    id: Optional[int] = None
    start_ts: Optional[int] = None
    end_ts: Optional[int] = None
    cwd: Optional[str] = None
    doc_text: Optional[str] = None

    @property
    def command_count(self) -> int:
        return len(self.commands)

    def to_document(self) -> str:
        """Build the text that gets embedded for this session.

        Includes the basename of the working directory (a weak but useful
        signal, e.g. ``nginx`` / ``myproject``) followed by the commands in
        order. This is the single source of truth for how a session is turned
        into embeddable text; the grouper and indexer must both use it.
        """
        lines: List[str] = []
        if self.cwd and self.cwd != UNKNOWN_CWD:
            base = os.path.basename(self.cwd.rstrip("/")) or self.cwd
            lines.append(f"directory: {base}")
        lines.extend(c.raw_cmd for c in self.commands)
        return "\n".join(lines)


@dataclass
class SearchResult:
    """A ranked session returned from a query.

    Attributes:
        session: The matched session (with its commands hydrated).
        score: Similarity score (higher is more relevant).
        matched_indices: Indices into ``session.commands`` that best match the
            query, used by the output layer to highlight the relevant commands.
    """

    session: Session
    score: float
    matched_indices: List[int] = field(default_factory=list)
