---
name: cli-output
model: claude-sonnet-5-thinking-high
description: Implements hist/cli.py and hist/output.py - the CLI entry point and rich result formatting.
---

You own ONLY: `hist/cli.py`, `hist/output.py`, and `tests/test_cli.py`. Do not
edit other files. Available merged modules: `hist.indexer.build_index_from_history`,
`hist.search.search`, `hist.config.Config`, `hist.models.SearchResult`.

Implement in `hist/output.py`:
- `render_results(results: list[SearchResult], query: str, console=None) -> None`:
  use `rich` to print, per result: rank + similarity score, human-readable
  timestamp (from session.start_ts), working directory, and the session's commands
  with the matched command(s) (session.matched_indices) HIGHLIGHTED and the
  surrounding commands shown as dimmed context. Handle empty results gracefully.
- `format_timestamp(ts) -> str` helper.

Implement in `hist/cli.py` a `main()` entry point (referenced by the
`hist = hist.cli:main` console script). Behaviour:
- `hist index [--window N] [--rebuild]` -> run build_index_from_history, print a
  summary (counts + elapsed).
- `hist "<natural language query>"` (the common case; any non-subcommand args are
  joined into the query) -> run search and render results. Support `-k/--top-k`.
- `hist` with no args -> print brief help.
- If the index/db do not exist yet, print a friendly hint to run `hist index`.
You may use argparse (recommended for the bare-query UX) or click.

Tests (`tests/test_cli.py`): test `render_results` with a hand-built SearchResult
list (assert it prints without error and includes the matched command and cwd via
a captured rich Console with record=True), and test the CLI arg routing by calling
main() with monkeypatched indexer/search (no model needed). Run from worktree root:
`python -m pytest tests/test_cli.py -q`. All must pass. Commit on your branch.
Report: files changed, tests, pass/fail, blockers.
