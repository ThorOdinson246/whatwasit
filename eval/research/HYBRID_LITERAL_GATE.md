# Hybrid literal gate fix (2026-07-03)

**Branch:** `fix/hybrid-default`

## Change

Option B: Jaccard RRF + FTS fusion runs only when `looks_literal_query(query)` is
true. Intent-paraphrase queries use semantic scoring only (same as
`hybrid_search=False` for that path).

FTS fast-path for short literal queries is unchanged (lines 211–214 in `search.py`).

## Results (86 answerable queries)

| Path | P@1 | MRR | nDCG@5 |
|------|----:|----:|-------:|
| Broken hybrid (pre-fix) | 0.419 | 0.596 | 0.656 |
| Semantic-only reference | 0.535 | 0.700 | 0.751 |
| **Literal-gated hybrid (shipping)** | **0.535** | **0.700** | **0.751** |

Full recovery on the standard eval set.

## 11 hybrid-hurt queries

All **11** queries that lost P@1 under broken hybrid now match semantic-only ranks.

## Literal query value

| Set | Literal queries (`looks_literal_query`) | Hybrid benefit |
|-----|----------------------------------------:|----------------|
| 86 answerable (intent-paraphrase) | **0** | N/A — gate is a no-op here |
| 15 keyword-heavy breakout | **1** (`tmux new-session attach-session detach`) | FTS fast-path; semantic P@1 **1.000** |

Option A (`hybrid_search=False` entirely) would tie on the 86-query set but lose
literal FTS fast-path on keyword-heavy queries. Literal gate wins: same P@1 on
intent eval, retains keyword path.

## Recommendation

**Ship literal-gated hybrid as default.** No need for Option A.
