"""Groups parsed :class:`~hist.models.Command` objects into sessions.

A *session* is a contiguous run of commands the user ran while doing one
thing. We split the command stream into sessions using two independent
heuristics:

1. A time gap between consecutive commands larger than
   ``config.session_window_seconds``.
2. A change in working directory (when ``config.split_on_cwd_change`` is
   enabled).

Many history sources (plain bash/zsh history files) don't record the
working directory a command ran in. :func:`reconstruct_cwd` recovers it by
statically replaying ``cd``/``pushd``/``popd`` invocations found in the
command stream itself.
"""

from __future__ import annotations

import posixpath
import re
from typing import List, Optional, Tuple

from hist.config import Config
from hist.models import Command, Session

HOME = "~"
"""Sentinel representing the user's home directory in reconstructed paths."""

_UNRESOLVABLE_RE = re.compile(r"[$`*]")
"""Matches constructs we cannot resolve statically: variables ($FOO, $(...)),
command substitution (backticks), and globs (*)."""


def _looks_unresolvable(target: str) -> bool:
    return bool(_UNRESOLVABLE_RE.search(target))


def _first_arg(rest: str) -> str:
    """Extract just the first argument of a cd/pushd (its target directory).

    Shell ``cd`` takes a single path argument; history entries can carry extra
    tokens (multi-command lines, trailing junk from backslash-joined entries),
    which must not leak into the resolved directory. Honors simple quoting so a
    quoted path containing spaces stays intact.
    """
    s = rest.strip()
    if not s:
        return ""
    if s[0] in ("'", '"'):
        quote = s[0]
        end = s.find(quote, 1)
        return s[1:end] if end != -1 else s[1:]
    return s.split()[0]


def _resolve_target(rest: str, current: str) -> Optional[str]:
    """Resolve the argument of a ``cd``/``pushd`` invocation.

    Returns the new absolute-ish path, or ``None`` if it can't be resolved
    statically (the caller should then leave the current directory alone).
    """
    target = _first_arg(rest)
    if target == "" or target == "~":
        return HOME

    if _looks_unresolvable(target):
        return None

    # Home-relative paths ("~/sub") anchor under HOME without doubling the "~".
    if target == "~" or target.startswith("~/"):
        return posixpath.normpath(posixpath.join(HOME, target[2:]))

    if target.startswith("/"):
        return posixpath.normpath(target)

    if current == HOME:
        # Treat "~" as an opaque root; relative paths from home just nest
        # under it textually (e.g. "sub" -> "~/sub").
        return posixpath.normpath(posixpath.join(HOME, target))

    return posixpath.normpath(posixpath.join(current, target))


def _split_cd_command(raw_cmd: str) -> Optional[Tuple[str, str]]:
    """Split a raw command into ``(name, rest)`` if it's a cd/pushd/popd."""
    stripped = raw_cmd.strip()
    if not stripped:
        return None
    parts = stripped.split(None, 1)
    name = parts[0]
    if name not in ("cd", "pushd", "popd"):
        return None
    rest = parts[1] if len(parts) > 1 else ""
    return name, rest


def _apply_cd(
    raw_cmd: str,
    current: str,
    oldpwd: Optional[str],
    stack: List[str],
) -> Tuple[str, Optional[str]]:
    """Replay one command's effect on the directory stack.

    Mutates ``stack`` in place (push/pop). Returns the
    ``(new_current, new_oldpwd)`` pair to use for subsequent commands.
    """
    parsed = _split_cd_command(raw_cmd)
    if parsed is None:
        return current, oldpwd

    name, rest = parsed

    if name == "popd":
        if not stack:
            return current, oldpwd
        new_current = stack.pop()
        return new_current, current

    target = rest.strip()

    if name == "cd" and target == "-":
        if oldpwd is None:
            return current, oldpwd
        return oldpwd, current

    resolved = _resolve_target(rest, current)
    if resolved is None:
        return current, oldpwd

    if name == "pushd":
        stack.append(current)

    return resolved, current


def reconstruct_cwd(commands: List[Command], start_cwd: str = HOME) -> None:
    """Walk ``commands`` in order, filling in ``command.cwd`` in place.

    Only commands whose ``cwd`` is currently ``None`` are touched; commands
    that already carry a reliable cwd (e.g. from atuin) are left untouched
    but still used to (re)synchronize the tracked current directory.

    A ``cd``/``pushd``/``popd`` is attributed to the directory it *lands in*
    (its destination), not the directory it was launched from. This keeps the
    command that enters a directory inside that directory's session, instead of
    fragmenting every directory change into its own one-command session.
    """
    current = start_cwd
    oldpwd: Optional[str] = None
    stack: List[str] = []

    for cmd in commands:
        if cmd.cwd is not None:
            # Authoritative cwd (e.g. atuin): trust it as recorded, but still
            # replay this command's directory effect for the commands after it.
            current = cmd.cwd
            current, oldpwd = _apply_cd(cmd.raw_cmd, current, oldpwd, stack)
        else:
            # Reconstructed: apply the directory effect first, then label this
            # command with the resulting directory (destination for a cd).
            current, oldpwd = _apply_cd(cmd.raw_cmd, current, oldpwd, stack)
            cmd.cwd = current


def _session_cwd(group: List[Command]) -> Optional[str]:
    for cmd in group:
        if cmd.cwd is not None:
            return cmd.cwd
    return None


def _ts_bounds(group: List[Command]) -> Tuple[Optional[int], Optional[int]]:
    ts_values = [c.ts for c in group if c.ts is not None]
    if not ts_values:
        return None, None
    return min(ts_values), max(ts_values)


def _build_session(group: List[Command]) -> Session:
    start_ts, end_ts = _ts_bounds(group)
    session = Session(
        commands=list(group),
        start_ts=start_ts,
        end_ts=end_ts,
        cwd=_session_cwd(group),
    )
    session.doc_text = session.to_document()
    return session


def group_commands(commands: List[Command], config: Config) -> List[Session]:
    """Group an ordered list of commands into :class:`Session` objects.

    Commands lacking a ``cwd`` are first backfilled via
    :func:`reconstruct_cwd`. The stream is then split into sessions on a
    time gap exceeding ``config.session_window_seconds`` (only when both
    neighboring commands have timestamps) and/or a change of working
    directory (when ``config.split_on_cwd_change`` is enabled).
    """
    reconstruct_cwd(commands)

    sessions: List[Session] = []
    current_group: List[Command] = []
    prev: Optional[Command] = None

    for cmd in commands:
        if current_group and prev is not None:
            split = False

            if prev.ts is not None and cmd.ts is not None:
                if (cmd.ts - prev.ts) > config.session_window_seconds:
                    split = True

            if config.split_on_cwd_change and cmd.cwd != prev.cwd:
                split = True

            if split:
                sessions.append(_build_session(current_group))
                current_group = []

        current_group.append(cmd)
        prev = cmd

    if current_group:
        sessions.append(_build_session(current_group))

    return sessions
