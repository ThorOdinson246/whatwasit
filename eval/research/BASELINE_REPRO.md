# Eval baseline reproducibility — root cause (2026-07-03)

## Symptom

`eval/README.md` and `eval/summary.json` reported semantic P@1 **0.535**. A fresh
`run_eval.py` on unmodified `main` produced **0.419** — a 12-point gap with no code
changes on the branch.

## Root cause (confirmed)

**Stale eval artifacts, not non-determinism.**

| Evidence | Result |
|----------|--------|
| `eval/summary.json` last updated | commit `927fad5` (2026-06-30), **before** hybrid search |
| Hybrid search landed | `f1f08e2` (2026-07-02) — `feat(search): FTS keyword leg, literal fast path, lower hybrid gate` |
| `summary.json` per-query ranks vs fresh run | **22/86** queries differ; aggregate matches recomputed per-query |
| `hybrid_search=False` on current `main` | P@1 **0.5349** ×3 runs — **matches** `summary.json` exactly |
| `hybrid_search=True` (shipping default) | P@1 **0.4186** ×3 runs — **deterministic** |

The committed `summary.json` was generated when search was **semantic-only** (no hybrid
RRF). After `f1f08e2`, `Config.hybrid_search` defaults to `True` and the harness
calls the production `search()` path — but **nobody re-ran eval and updated the
canonical artifacts**.

README text (“gated hybrid RRF reranking”) described shipping behavior that the
**documented numbers did not include**.

## What is the TRUE current baseline?

**Shipping path** (`hybrid_search=True`, default): P@1 **0.419**, MRR **0.596**,
nDCG@5 **0.656** (86 answerable, MiniLM, 2026-07-03 repro).

**Semantic-only reference** (`hybrid_search=False`): P@1 **0.535**, MRR **0.700**,
nDCG@5 **0.751** — pre-hybrid metric, kept for regression comparison only.

Hybrid search **regresses** P@1 on this intent-paraphrase eval set (~−11.6 pp) while
keyword baseline is unchanged (0.291). The RRF fusion is reordering semantic neighbors
in ways that hurt top-1 on NL queries.

## Non-determinism

Ruled out. Three consecutive full index+query runs on `main` with each hybrid setting
produced identical P@1 to 4 decimal places.

## Fix applied (`fix/eval-baseline-repro`)

- Regenerated `eval/summary.json`, `eval/tables.md`, `eval/metrics_summary.csv` with
  `hybrid_search=True`
- Updated `eval/README.md` with shipping vs semantic-only rows
- `run_eval.py` now records `search_config.hybrid_search` in summary JSON

## Resolution (merged 2026-07-03)

1. **`fix/eval-baseline-repro`** — artifacts updated to broken-hybrid numbers (P@1 0.419).
2. **`fix/hybrid-default`** — hybrid RRF gated to literal queries only; P@1 **0.535**.
3. **`feature/richer-session-docs`** — universal doc enrichment; P@1 **0.547**.

See [README.md](README.md) for the full index of investigation write-ups.
