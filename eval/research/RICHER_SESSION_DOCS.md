# Richer session documents — universal enrichment (re-measured)

**Branch:** `feature/richer-session-docs`  
**Baseline:** hybrid shipping path P@1 **0.419** (`main` @ `fe2a235`)  
**Variant:** Universal enrichment, **git workflow sessions excluded** (≥2 `git` commands)

Sparse-only dropped — dominated by universal on every metric at equal Mode B cost.

## Results vs hybrid baseline

| Slice | n | Baseline | Universal−git | Δ |
|-------|--:|---------:|--------------:|--:|
| **Full** | 86 | 0.419 | **0.453** | **+0.035** |
| **Mode C** | 20 | 0.150 | **0.250** | **+0.100** |
| **Mode B** | 8 | 0.250 | **0.125** | **−0.125** |

Artifact: `eval/summary_v5.json` (2026-07-03).

## Excluding git sessions from enrichment pool

**Hypothesis:** Mode B regression came from enriching git workflow docs.  
**Result:** **Not confirmed.** Excluding git sessions (rebase/merge/undo/purge) does
**not** restore Mode B — still **0.125** (−0.125 vs baseline).

Git sessions keep baseline doc shape, but enriching **other** sessions still shifts
the shared embedding index and hybrid RRF rankings. Example collateral: `git-undo`
query rank 2→4 despite git session docs unchanged.

## Cross-contamination (unchanged mechanism)

See `eval/research/HYBRID_SEARCH_INVESTIGATION.md` — hybrid Jaccard RRF is the
largest accuracy problem (−0.116 P@1 vs semantic-only). Doc enrichment operates in
the same shared vector space; fixing Mode B via doc gating alone is insufficient
while hybrid default remains.

## Recommendation

**Do not merge** universal enrichment until:

1. Hybrid default is fixed or disabled (semantic-only restores 0.535), **and**
2. Mode B regression is re-checked on semantic-only baseline

If proceeding later: **universal−git** is the preferred enrichment variant
(+0.035 full, +0.100 Mode C) over sparse-only.

## Implementation

`whatwasit/models.py`: `_should_enrich_session()` — enrich all non-git workflows;
`_is_git_workflow_session()` skips sessions with ≥2 `git` commands.
