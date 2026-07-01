"""Core data models shared across every module.

These dataclasses are the frozen contract between the parser, grouper, indexer,
search, and output layers. Changing their public shape is a cross-module change.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

UNKNOWN_CWD = "?"
"""Sentinel for a working directory that could not be reconstructed."""

# ---------------------------------------------------------------------------
# Semantic expansion hints for terse commands (Fix 2: richer session docs).
#
# Each entry is (pattern, hint) where *pattern* is a substring matched
# case-insensitively against the joined command text.  Hits are appended as
# a single "context:" line so the embedding sees natural-language expansions
# alongside the raw commands — without fabricating anything that isn't
# already implied by the commands themselves.
# ---------------------------------------------------------------------------
_COMMAND_HINTS: List[Tuple[str, str]] = [
    # Python / virtualenv
    ("-m venv",           "python virtual environment isolation sandbox"),
    ("pip install",       "install python packages dependencies"),
    ("pip freeze",        "python packages list requirements freeze"),
    ("pip check",         "python package version conflict"),
    ("cProfile",          "python profiling performance slow hotspot"),
    ("snakeviz",          "profiling visualization flame graph performance"),
    ("pstats",            "profiling statistics performance hotspot"),
    # Git operations
    ("rebase -i",         "interactive rebase replay commits history"),
    ("rebase --continue", "rebase continue after conflict"),
    ("filter-branch",     "git history rewrite purge scrub secret"),
    ("git revert",        "undo rollback commit history"),
    ("git reflog",        "git history recovery undo"),
    # Docker
    ("docker volume",     "docker data persist survive container restart"),
    ("docker network",    "docker container networking bridge connect"),
    ("docker compose",    "docker multi service stack orchestrate"),
    ("docker-compose",    "docker multi service stack orchestrate"),
    ("docker system df",  "docker disk space cleanup prune"),
    ("image prune",       "docker cleanup remove dangling images"),
    # npm / Node
    ("npm audit",         "javascript security vulnerability package patch"),
    ("npm cache",         "javascript npm cache corrupt rebuild"),
    ("--legacy-peer-deps","npm package dependency conflict version mismatch"),
    # SSH
    ("ssh-keygen",        "ssh key generate authentication credentials"),
    ("ssh-copy-id",       "ssh key passwordless login authorized"),
    ("ssh -A",            "ssh agent forwarding jump host tunnel"),
    ("authorized_keys",   "ssh key permission access"),
    # Cron / scheduling
    ("crontab",           "cron schedule timer recurring automatic task"),
    # System services
    ("systemctl",         "service daemon background process start stop"),
    ("journalctl",        "service log output daemon debug"),
    ("logrotate",         "log rotation disk space size management"),
    ("certbot",           "ssl certificate https tls renew letsencrypt"),
    # Permissions
    ("chmod",             "file permission access bits execute allowed"),
    ("chown",             "file ownership user group"),
    # Network / DNS
    ("resolvectl",        "dns cache flush nameserver records resolve"),
    ("nslookup",          "dns lookup resolve address nameserver"),
    (" dig ",             "dns lookup resolve nameserver query"),
    ("lsof -i",           "port process occupy free kill listen"),
    # Archiving
    ("tar czf",           "archive compress bundle pack folder"),
    ("tar xzf",           "archive extract unpack decompress"),
    ("tar tzf",           "archive list contents inspect"),
    # Text / file processing
    ("sed -i",            "find replace text bulk rename across files"),
    ("xargs sed",         "bulk text replace across files"),
    # Database migrations
    ("alembic upgrade",   "database migration schema apply up"),
    ("alembic downgrade", "database migration schema rollback"),
    ("pg_hba.conf",       "postgres authentication connection refused"),
    # Terminal multiplexer
    ("tmux",              "terminal session persist reconnect detach"),
    # HTTP / API inspection
    ("curl ",             "http api request response inspect endpoint"),
    ("| jq",              "json parse api response format"),
    # File transfer
    ("rsync",             "file sync copy transfer remote mirror"),
    # Encryption
    ("gpg -c",            "encrypt file passphrase secure protect"),
    ("gpg -d",            "decrypt file passphrase"),
    # Kubernetes
    ("kubectl",           "kubernetes pod cluster container orchestrator"),
]


def _collect_hints(cmds: List[str]) -> List[str]:
    """Return semantic expansion hints that match the given command list.

    Scans the joined lower-cased command text for each pattern; duplicate
    hint strings are suppressed so the context line stays compact.
    """
    text = " ".join(cmds).lower()
    seen: set = set()
    hints: List[str] = []
    for pattern, hint in _COMMAND_HINTS:
        if pattern.lower() in text and hint not in seen:
            seen.add(hint)
            hints.append(hint)
    return hints


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

        Includes the basename of the working directory followed by the raw
        commands, then appends a compact "context:" line with semantic
        expansion hints for any recognised abbreviated commands (e.g.
        ``pip install`` → "install python packages dependencies").  The hints
        add natural-language signal without fabricating content — each hint is
        an established description of what the matched command does.

        This is the single source of truth for how a session is turned into
        embeddable text; the grouper and indexer must both use it.
        """
        lines: List[str] = []
        if self.cwd and self.cwd != UNKNOWN_CWD:
            base = os.path.basename(self.cwd.rstrip("/")) or self.cwd
            lines.append(f"directory: {base}")
        cmd_lines = [c.raw_cmd for c in self.commands]
        lines.extend(cmd_lines)
        hints = _collect_hints(cmd_lines)
        if hints:
            lines.append("context: " + "; ".join(hints))
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
