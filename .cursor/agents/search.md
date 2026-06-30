---
name: search
model: claude-sonnet-5-thinking-high
description: Implements hist/search.py - query embedding, nearest-neighbour search, result hydration.
---

You own ONLY: `hist/search.py` and `tests/test_search.py`. Do not edit other
files. Available merged modules: `hist.embedder.build_embedder`,
`hist.index.build_index`, `hist.db`, `hist.config.Config`,
`hist.models.{Session,Command,SearchResult}`, `hist.interfaces`.

Implement in `hist/search.py`:
- `search(config, query, *, k=None, embedder=None, index=None) -> list[SearchResult]`:
  encode the query (embedder.encode_one) -> index.load() -> index.search(vec, k or
  config.top_k) -> for each (session_id, score): db.get_session -> build a
  SearchResult. Compute `matched_indices`: encode the session's command strings and
  pick the indices whose cosine to the query is highest (top 1-3, and/or above a
  small margin). Keep this cheap (only for returned sessions). Sort results by
  score descending. Open the DB read-only via db.connect(config.db_path).
- Allow embedder/index injection for tests.

Tests (`tests/test_search.py`): use a FakeEmbedder (deterministic vectors keyed by
keyword presence, no model) + temp Config; seed the DB and index with 3 sessions on
different topics via the indexer or directly; assert the right session ranks #1 for
a matching query and that matched_indices points at a sensible command. Run from
worktree root: `python -m pytest tests/test_search.py -q`. All must pass. Commit on
your branch. Report: files changed, tests, pass/fail, blockers.
