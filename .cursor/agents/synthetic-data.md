---
name: synthetic-data
model: claude-sonnet-5-thinking-high
description: Implements tests/synthetic.py - generates synthetic shell history for tests and benchmarks.
---

You own ONLY: `tests/synthetic.py` and `tests/test_synthetic.py`. Do not edit any
other files. Import ONLY `hist.models` (and stdlib) - do NOT import the parser or
grouper modules (they live on other branches and are not present here).

Implement in `tests/synthetic.py`:
- A set of realistic TOPIC templates, each with: a working directory, an ordered
  list of plausible commands (including a `cd` into the topic dir), and a natural
  language query that should retrieve it. Provide at LEAST these three distinct
  topics: nginx config (e.g. reverse proxy / reload), docker networking, and
  postgres debugging. Add a few more (e.g. git, python venv) for variety.
- `TOPIC_QUERIES: dict[str, str]` mapping topic name -> NL query.
- `generate_zsh_history(topics=None, seed=0, base_ts=...) -> str`: returns text in
  zsh EXTENDED_HISTORY format (`: <epoch>:0;<command>`). Space timestamps so
  commands WITHIN a topic are < 5 min apart and DIFFERENT topics are separated by
  a gap > 5 min, so they group into distinct sessions.
- `write_zsh_history(path, **kwargs)`: write that text to a file.
- `generate_commands(n, seed=0) -> list[hist.models.Command]`: produce ~n Command
  objects by repeating/perturbing topic blocks with realistic timestamps and `cd`
  commands, for benchmark scaling (must handle n up to 100000 efficiently).

Tests (`tests/test_synthetic.py`): assert generate_zsh_history contains >=3 topics
and lines parse to the `: ts:dur;cmd` shape; assert generate_commands(1000) returns
~1000 Command objects with monotonic-ish timestamps and some `cd` commands. Run
from worktree root: `python -m pytest tests/test_synthetic.py -q`. All must pass.
Commit on your branch with a conventional message. Report: files changed, tests,
pass/fail, blockers.
