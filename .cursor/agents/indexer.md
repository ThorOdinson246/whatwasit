---
name: indexer
model: claude-sonnet-5-thinking-high
description: Implements hist/indexer.py - the parse -> group -> persist -> embed -> index pipeline.
---

You own ONLY: `hist/indexer.py` and `tests/test_indexer.py`. Do not edit other
files. These modules already exist and are merged: `hist.parsers` (load_all),
`hist.sessions.group_commands`, `hist.embedder.build_embedder`,
`hist.index.build_index`, `hist.db`, `hist.config.Config`, `hist.models`.

Implement in `hist/indexer.py`:
- `@dataclass IndexStats(n_commands, n_sessions, elapsed_seconds)`.
- `index_commands(config, commands, *, embedder=None, index=None, reset=True) -> IndexStats`:
  group commands -> open db (db.connect/initialize; if reset, db.reset) -> insert
  each session (db.insert_session sets session.id) -> batch-encode all session
  doc_texts with the embedder -> index.add(session_ids, vectors) -> index.save().
  Allow embedder/index injection for tests; otherwise build from config.
- `build_index_from_history(config, *, embedder=None, index=None) -> IndexStats`:
  parsers.load_all(config) then index_commands(...).

Tests (`tests/test_index_pipeline` -> file `tests/test_indexer.py`): use a tiny
FakeEmbedder (subclass hist.interfaces.Embedder returning deterministic vectors,
no model needed) and a temp Config (data_dir in tmp_path) to index a small set of
Commands, then assert db.count_sessions matches and len(index) matches n_sessions.
Run from worktree root: `python -m pytest tests/test_indexer.py -q`. All must
pass. Commit on your branch. Report: files changed, tests, pass/fail, blockers.
