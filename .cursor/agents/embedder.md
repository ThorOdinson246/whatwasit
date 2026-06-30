---
name: embedder
model: claude-sonnet-5-thinking-high
description: Implements hist/embedder.py - FastEmbedEmbedder behind the Embedder ABC.
---

You own ONLY: `hist/embedder.py` and `tests/test_embedder.py`. Do not edit any
other files.

Frozen contracts (import them): `hist.interfaces.Embedder`, `hist.config.Config`.

Implement in `hist/embedder.py`:
- `class FastEmbedEmbedder(Embedder)`:
  - `__init__(self, model_name: str = Config().model_name, dim: int = 384,
    cache_dir: str | None = None)`. Lazy-initialize the underlying
    `fastembed.TextEmbedding` on first `encode` (do not load the model in
    `__init__`, so construction is cheap and import-safe).
  - `dim` property returns the dimensionality.
  - `encode(self, texts) -> np.ndarray`: returns float32 array shape
    `(len(texts), dim)`, L2-normalized rows. Handle empty input -> shape
    `(0, dim)`. fastembed already L2-normalizes; still cast to float32 and
    re-normalize defensively.
- `build_embedder(config: Config) -> Embedder` factory.

The model `sentence-transformers/all-MiniLM-L6-v2` is ALREADY cached locally.
Run tests fully offline by setting env `HF_HUB_OFFLINE=1` and
`TRANSFORMERS_OFFLINE=1`. Do NOT require network.

Tests (`tests/test_embedder.py`): assert encode of 2 strings -> shape (2, 384),
dtype float32, row norms ~1.0; empty list -> (0, 384); and a semantic sanity
check: cosine(similar pair) > cosine(dissimilar pair). Run from worktree root:
`HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python -m pytest tests/test_embedder.py -q`.
All must pass. Commit on your branch with a conventional message. Report: files
changed, tests, pass/fail, blockers.
