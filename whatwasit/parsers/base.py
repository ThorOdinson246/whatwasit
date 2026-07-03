"""Abstract parser interface plus source discovery and aggregation.

Concrete parsers (zsh/bash/atuin) live in sibling modules. This module ties
them together: it knows where each shell's history file conventionally
lives, and how to combine whichever ones are actually present on disk into a
single flat list of :class:`~whatwasit.models.Command`.
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator, List, Tuple

from ..config import Config
from ..models import Command


class HistoryParser(ABC):
    """Turns a history file/db at ``path`` into a stream of :class:`Command`."""

    @abstractmethod
    def parse(self, path: Path | str) -> Iterator[Command]:
        """Yield commands found at ``path``. Must not raise on malformed input."""


def default_sources() -> List[Tuple[Path, str]]:
    """Return candidate ``(path, kind)`` pairs for the well-known shell histories.

    ``kind`` is one of ``"zsh"``, ``"bash"``, ``"atuin"``. Callers should check
    existence themselves; this function only describes conventional locations.
    """
    home = Path.home()
    return [
        (home / ".zsh_history", "zsh"),
        (home / ".bash_history", "bash"),
        (home / ".local" / "share" / "atuin" / "history.db", "atuin"),
    ]


def load_all(config: Config) -> List[Command]:
    """Detect which default history sources exist and parse all of them.

    Atuin is only consulted if its database file actually exists. Sources
    that don't exist are silently skipped. ``config`` is accepted for API
    symmetry with the rest of the codebase (e.g. future overridable paths)
    even though the current implementation only needs default locations.
    """
    from . import atuin as atuin_mod
    from . import bash as bash_mod
    from . import zsh as zsh_mod

    del config  # not yet used to override source locations

    commands: List[Command] = []
    for path, kind in default_sources():
        if not path.exists():
            continue
        if kind == "zsh":
            commands.extend(zsh_mod.parse_zsh(path))
        elif kind == "bash":
            commands.extend(bash_mod.parse_bash(path))
        elif kind == "atuin":
            commands.extend(atuin_mod.parse_atuin(path))
    return commands


def history_fingerprint() -> str:
    """Stable hash of default history source mtimes and sizes for incremental index."""
    parts: List[dict[str, object]] = []
    for path, _kind in default_sources():
        if not path.exists():
            continue
        stat = path.stat()
        parts.append(
            {
                "path": str(path),
                "mtime_ns": stat.st_mtime_ns,
                "size": stat.st_size,
            }
        )
    payload = json.dumps(parts, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
