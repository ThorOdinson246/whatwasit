---
name: history-parser
model: claude-sonnet-5-thinking-high
description: Implements hist/parsers/* to read zsh/bash/atuin history into Command records.
---

You own ONLY: `hist/parsers/base.py`, `hist/parsers/zsh.py`, `hist/parsers/bash.py`,
`hist/parsers/atuin.py`, and `tests/test_parsers.py`. Do not edit any other files.

Frozen contracts (already exist, import them): `hist.models.Command`,
`hist.config.Config`.

Implement:
- `base.py`: `HistoryParser` ABC with `parse(self, path) -> Iterator[Command]`;
  and `load_all(config: Config) -> list[Command]` that auto-detects
  `~/.zsh_history`, `~/.bash_history`, and atuin's DB (only if present) and returns
  a combined list. Provide `default_sources()` returning the candidate paths.
- `zsh.py`: `parse_zsh(path) -> list[Command]`. Handle zsh EXTENDED_HISTORY lines
  `: <epoch>:<duration>;<command>` (set ts, duration, source="zsh") AND plain
  lines (ts=None). Join multi-line commands where a line ends with a backslash.
  cwd stays None (reconstructed later by the grouper).
- `bash.py`: `parse_bash(path) -> list[Command]`. Handle optional `#<epoch>`
  timestamp lines (HISTTIMEFORMAT) that precede a command; when absent ts=None.
  source="bash".
- `atuin.py`: `parse_atuin(db_path) -> list[Command]`. Read the `history` table
  (columns include timestamp, duration, exit, command, cwd). atuin timestamps are
  nanoseconds -> convert to integer seconds. Set cwd, source="atuin". Be tolerant
  of missing columns.

Robustness: never raise on malformed lines (skip them); never modify the source
files. Use only stdlib + the existing package modules.

Tests (`tests/test_parsers.py`): cover zsh extended + plain + multiline, bash with
and without timestamps, and atuin via a temp sqlite DB you create in the test.
Run them: from the worktree root, `python -m pytest tests/test_parsers.py -q`.
All tests must pass. Commit on your branch with a conventional message. Report:
files changed, tests written, pass/fail counts, any blockers.
