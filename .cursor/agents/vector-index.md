---
name: vector-index
model: claude-sonnet-5-thinking-high
description: Implements hist/index.py - UsearchIndex behind the VectorIndex ABC.
---

You own ONLY: `hist/index.py` and `tests/test_index.py`. Do not edit any other
files.

Frozen contracts (import them): `hist.interfaces.VectorIndex`, `hist.config.Config`.

Implement in `hist/index.py` using the `usearch` package
(`from usearch.index import Index`):
- `class UsearchIndex(VectorIndex)`:
  - `__init__(self, path, dim, metric="cos")`: create
    `Index(ndim=dim, metric=metric, dtype="f32")`. Store path.
  - `add(keys, vectors)`: accept a sequence of int keys and a float32 ndarray
    `(n, dim)`; coerce dtype/shape as needed.
  - `search(vector, k) -> list[tuple[int, float]]`: accept shape `(dim,)` or
    `(1, dim)`; return up to k `(key, score)` pairs, best first, where score is a
    SIMILARITY (for cos, score = 1 - distance), highest first.
  - `save()`: persist to `path` (create parent dir).
  - `load()`: if the file exists, load it; otherwise leave the index empty.
  - `__len__`: number of vectors.
- `build_index(config: Config) -> VectorIndex` factory using `config.index_path`
  and `config.embedding_dim`.

Use only `usearch` + numpy + stdlib + existing package modules.

Tests (`tests/test_index.py`): add ~10 random normalized vectors with int keys;
assert a query equal to one stored vector returns that key first with score ~1.0;
assert top-k ordering; assert save()/load() roundtrip preserves results into a new
instance; assert `len()`. Run from worktree root:
`python -m pytest tests/test_index.py -q`. All must pass. Commit on your branch
with a conventional message. Report: files changed, tests, pass/fail, blockers.
