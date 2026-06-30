---
name: session-grouper
model: claude-sonnet-5-thinking-high
description: Implements hist/sessions.py - groups Commands into Sessions by time gap + reconstructed cwd.
---

You own ONLY: `hist/sessions.py` and `tests/test_sessions.py`. Do not edit any
other files.

Frozen contracts (import them): `hist.models.Command`, `hist.models.Session`,
`hist.models.UNKNOWN_CWD`, `hist.config.Config`.

Implement in `hist/sessions.py`:
- `reconstruct_cwd(commands: list[Command], start_cwd: str = "~") -> None`:
  replay the command stream and SET `command.cwd` on each command (in place).
  Track current dir, replaying `cd`, `cd ~`/`cd` (-> home "~"), `cd -` (-> OLDPWD),
  `cd /abs`, `cd rel` (posixpath.normpath join), `pushd X`, `popd`. If a target
  cannot be statically resolved (contains `$`, backticks, `*`, command
  substitution, or quoting around variables) keep the current dir unchanged. Do
  NOT touch commands whose cwd is already set (e.g. atuin-sourced).
- `group_commands(commands: list[Command], config: Config) -> list[Session]`:
  first call reconstruct_cwd for commands lacking cwd, then walk in order and
  start a NEW session when: the inter-command time gap exceeds
  `config.session_window_seconds` (only when both have ts), OR
  (`config.split_on_cwd_change` and the cwd differs from the previous command).
  When commands have no timestamps, split on cwd change only. For each Session set
  `commands`, `start_ts`/`end_ts` (min/max of present ts, else None), `cwd` (the
  session's directory), and `doc_text = session.to_document()`.

Keep commands in their original order. Use only stdlib + existing package modules.

Tests (`tests/test_sessions.py`): build synthetic Command lists and assert:
cwd reconstruction for cd/relative/pushd-popd/`cd -`; a time gap > window splits a
session; a cwd change splits a session; commands without timestamps split on cwd
only; session.cwd / start_ts / end_ts are correct. Run from worktree root:
`python -m pytest tests/test_sessions.py -q`. All must pass. Commit on your branch
with a conventional message. Report: files changed, tests, pass/fail, blockers.
