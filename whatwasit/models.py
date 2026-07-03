"""Core data models shared across every module.

These dataclasses are the frozen contract between the parser, grouper, indexer,
search, and output layers. Changing their public shape is a cross-module change.
"""

from __future__ import annotations

import os
import re
import shlex
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

UNKNOWN_CWD = "?"
"""Sentinel for a working directory that could not be reconstructed."""

# Patterns shipped before richer-doc enrichment (applied to every session).
_BASIC_COMMAND_HINTS: List[Tuple[str, str]] = [
    ("-m venv",           "python virtual environment isolation sandbox"),
    ("pip install",       "install python packages dependencies"),
    ("pip freeze",        "python packages list requirements freeze"),
    ("pip check",         "python package version conflict"),
    ("cProfile",          "python profiling performance slow hotspot"),
    ("snakeviz",          "profiling visualization flame graph performance"),
    ("pstats",            "profiling statistics performance hotspot"),
    ("rebase -i",         "interactive rebase replay commits history"),
    ("rebase --continue", "rebase continue after conflict"),
    ("filter-branch",     "git history rewrite purge scrub secret"),
    ("git revert",        "undo rollback commit history"),
    ("git reflog",        "git history recovery undo"),
    ("docker volume",     "docker data persist survive container restart"),
    ("docker network",    "docker container networking bridge connect"),
    ("docker compose",    "docker multi service stack orchestrate"),
    ("docker-compose",    "docker multi service stack orchestrate"),
    ("docker system df",  "docker disk space cleanup prune"),
    ("image prune",       "docker cleanup remove dangling images"),
    ("npm audit",         "javascript security vulnerability package patch"),
    ("npm cache",         "javascript npm cache corrupt rebuild"),
    ("--legacy-peer-deps","npm package dependency conflict version mismatch"),
    ("ssh-keygen",        "ssh key generate authentication credentials"),
    ("ssh-copy-id",       "ssh key passwordless login authorized"),
    ("ssh -A",            "ssh agent forwarding jump host tunnel"),
    ("authorized_keys",   "ssh key permission access"),
    ("crontab",           "cron schedule timer recurring automatic task"),
    ("systemctl",         "service daemon background process start stop"),
    ("journalctl",        "service log output daemon debug"),
    ("logrotate",         "log rotation disk space size management"),
    ("certbot",           "ssl certificate https tls renew letsencrypt"),
    ("chmod",             "file permission access bits execute allowed"),
    ("chown",             "file ownership user group"),
    ("resolvectl",        "dns cache flush nameserver records resolve"),
    ("nslookup",          "dns lookup resolve address nameserver"),
    (" dig ",             "dns lookup resolve nameserver query"),
    ("lsof -i",           "port process occupy free kill listen"),
    ("tar czf",           "archive compress bundle pack folder"),
    ("tar xzf",           "archive extract unpack decompress"),
    ("tar tzf",           "archive list contents inspect"),
    ("sed -i",            "find replace text bulk rename across files"),
    ("xargs sed",         "bulk text replace across files"),
    ("alembic upgrade",   "database migration schema apply up"),
    ("alembic downgrade", "database migration schema rollback"),
    ("pg_hba.conf",       "postgres authentication connection refused"),
    ("tmux",              "terminal session persist reconnect detach"),
    ("curl ",             "http api request response inspect endpoint"),
    ("| jq",              "json parse api response format"),
    ("rsync",             "file sync copy transfer remote mirror"),
    ("gpg -c",            "encrypt file passphrase secure protect"),
    ("gpg -d",            "decrypt file passphrase"),
    ("kubectl",           "kubernetes pod cluster container orchestrator"),
]

# Extra patterns for terse sessions only (Mode C fix).
_SPARSE_COMMAND_HINTS: List[Tuple[str, str]] = [
    (".venv/bin/activate", "activate python virtual environment"),
    ("bin/activate",      "activate python virtual environment"),
    ("requirements.txt",  "python project dependencies requirements file"),
    ("$path",             "shell PATH environment executable search lookup"),
    (".bashrc",           "shell startup profile environment variables persist"),
    (".zshrc",            "shell startup profile environment variables persist"),
    (".profile",          "shell startup profile environment variables persist"),
    ("which ",            "locate executable command in PATH"),
    ("echo $path",        "print PATH environment variable"),
    ("find ",             "search files filesystem directory tree"),
    ("-size +",           "large files disk space threshold"),
    ("-mtime +",          "old files modification age"),
    ("-name '*.tmp'",     "temporary files cleanup delete"),
    ("git rm --cached",   "remove tracked file from git history index"),
    ("git gc",            "git repository garbage collect cleanup"),
    ("--force --all",     "force push rewritten git history remote"),
    ("volume inspect",    "docker named volume storage inspect"),
    ("-v ",               "docker volume mount bind persist data"),
    ("--volume",          "docker volume mount bind persist data"),
    ("/var/lib/postgresql", "postgres database data directory persist"),
    ("volume prune",      "docker cleanup remove unused volumes"),
    ("sites-available",   "nginx site virtual host reverse proxy config"),
    ("nginx -t",          "nginx configuration syntax test"),
    ("systemctl reload nginx", "reload nginx reverse proxy web server"),
]

_BINARY_EXPANSIONS: dict[str, str] = {
    "python": "python interpreter",
    "python3": "python interpreter",
    "pip": "python package manager pip",
    "pip3": "python package manager pip",
    "which": "locate executable in PATH",
    "find": "search files in directory tree",
    "nginx": "nginx web server reverse proxy",
    "crontab": "cron job scheduler",
    "docker": "docker container runtime",
    "kubectl": "kubernetes cluster CLI",
    "git": "git version control",
    "vim": "text editor config file",
    "nano": "text editor config file",
    "curl": "http client request test",
    "alembic": "database schema migration tool",
    "npm": "javascript node package manager",
    "node": "javascript node runtime",
    "systemctl": "linux systemd service manager",
    "journalctl": "systemd service logs",
    "tar": "archive compress extract files",
    "rsync": "remote file sync copy",
    "gpg": "encryption gpg tool",
    "ssh": "secure shell remote login",
    "ssh-keygen": "ssh key generation",
    "tmux": "terminal multiplexer session",
    "sed": "stream editor text replace",
    "chmod": "change file permissions",
    "chown": "change file ownership",
    "source": "load shell script environment",
    "pg_isready": "postgres server readiness check",
    "psql": "postgres interactive SQL client",
}


def _format_cwd_lines(cwd: str, *, extended: bool) -> List[str]:
    """Directory basename; path tail only for sparse sessions."""
    base = os.path.basename(cwd.rstrip("/")) or cwd
    lines = [f"directory: {base}"]
    if not extended:
        return lines
    normalized = cwd.strip()
    if normalized.startswith("~/"):
        tail = normalized[2:].strip("/")
    elif normalized.startswith("/"):
        parts = [p for p in normalized.strip("/").split("/") if p]
        tail = "/".join(parts[-2:]) if len(parts) > 1 else (parts[0] if parts else "")
    else:
        tail = normalized.strip("/")
    if tail and tail != base:
        lines.append(f"path: {tail}")
    return lines


def _command_binary(cmd: str) -> Optional[str]:
    stripped = cmd.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if stripped.startswith("source ") or stripped.startswith("."):
        return "source"
    try:
        tokens = shlex.split(stripped)
    except ValueError:
        tokens = stripped.split()
    skip = {"sudo", "env", "nohup", "time", "command", "builtin"}
    for tok in tokens:
        if tok in skip:
            continue
        if tok.startswith("-") or "=" in tok:
            continue
        return os.path.basename(tok)
    return None


def _collect_tool_lines(cmds: List[str]) -> List[str]:
    seen_bins: set[str] = set()
    parts: List[str] = []
    for cmd in cmds:
        binary = _command_binary(cmd)
        if binary is None or binary in seen_bins:
            continue
        seen_bins.add(binary)
        expansion = _BINARY_EXPANSIONS.get(binary)
        if expansion:
            parts.append(f"{binary} ({expansion})")
        else:
            parts.append(binary)
    if not parts:
        return []
    return ["tools: " + "; ".join(parts)]


def _collect_flag_hints(cmds: List[str]) -> List[str]:
    lower = " ".join(cmds).lower()
    hints: List[str] = []
    seen: set[str] = set()

    def add(hint: str) -> None:
        if hint not in seen:
            seen.add(hint)
            hints.append(hint)

    if re.search(r"-size\s+\+", lower):
        add("large files disk space threshold")
    if re.search(r"-mtime\s+\+", lower):
        add("old files modification age")
    if re.search(r"docker\s+run\b", lower) and re.search(r"\s-v\s|--volume", lower):
        add("docker volume mount persist container data")
    if "postgres" in lower and ("docker run" in lower or "volume" in lower):
        add("postgres database container data persist")
    if re.search(r"git\s+filter-branch", lower):
        add("rewrite git history remove file every revision")
    if re.search(r"git\s+push\b.*--force", lower):
        add("force push rewritten git history remote")
    return hints


def _collect_hints_from(patterns: List[Tuple[str, str]], cmds: List[str]) -> List[str]:
    text = " ".join(cmds).lower()
    seen: set[str] = set()
    hints: List[str] = []
    for pattern, hint in patterns:
        if pattern.lower() in text and hint not in seen:
            seen.add(hint)
            hints.append(hint)
    return hints


# Substrings that identify terse Mode-C-style sessions worth enriching.
_SPARSE_SESSION_MARKERS: Tuple[str, ...] = (
    "-m venv",
    ".venv",
    "bin/activate",
    "$path",
    ".bashrc",
    ".zshrc",
    "which ",
    "cprofile",
    "snakeviz",
    "pip check",
    "find ",
    "-size +",
    "-mtime +",
    "sites-available",
    "nginx -t",
    "crontab",
    "filter-branch",
    "volume inspect",
    "docker system df",
)


def _is_sparse_session(cmds: List[str]) -> bool:
    """True when commands match a known terse-doc pattern (Mode C fix)."""
    if not cmds:
        return False
    text = " ".join(cmds).lower()
    if not any(marker in text for marker in _SPARSE_SESSION_MARKERS):
        return False
    total = sum(len(c) for c in cmds)
    return len(cmds) <= 6 and total <= 250


def _collect_hints(cmds: List[str], *, sparse: bool) -> List[str]:
    patterns = list(_BASIC_COMMAND_HINTS)
    if sparse:
        patterns.extend(_SPARSE_COMMAND_HINTS)
    hints = _collect_hints_from(patterns, cmds)
    if sparse:
        seen = set(hints)
        for hint in _collect_flag_hints(cmds):
            if hint not in seen:
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

        Terse sessions (short command lists with little semantic signal) get
        extra enrichment: path tail, tool-name expansions, and additional
        context hints derived from flags and arguments.  All other sessions keep
        the pre-enrichment document shape so sibling-topic ranking is unchanged.
        """
        cmd_lines = [c.raw_cmd for c in self.commands]
        sparse = _is_sparse_session(cmd_lines)
        lines: List[str] = []
        if self.cwd and self.cwd != UNKNOWN_CWD:
            lines.extend(_format_cwd_lines(self.cwd, extended=sparse))
        if sparse:
            lines.extend(_collect_tool_lines(cmd_lines))
        lines.extend(cmd_lines)
        hints = _collect_hints(cmd_lines, sparse=sparse)
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
