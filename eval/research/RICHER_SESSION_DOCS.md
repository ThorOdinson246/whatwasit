# Richer session documents — universal enrichment (re-measured)

**Branch:** `feature/richer-session-docs`  
**Baseline:** literal-gated hybrid P@1 **0.535** (`fix/hybrid-default` / `summary_v6.json`)  
**Variant:** Universal enrichment, **git workflow sessions excluded** (≥2 `git` commands)

Sparse-only dropped — dominated by universal on every metric at equal Mode B cost.

## Results vs gated-hybrid baseline

| Slice | n | Gated baseline | Universal−git | Δ |
|-------|--:|---------------:|--------------:|--:|
| **Full** | 86 | 0.535 | **0.547** | **+0.012** |
| **Mode C** | 20 | 0.200 | **0.250** | **+0.050** |
| **Mode B** | 8 | 0.500 | **0.500** | **0.000** |

Artifact: `eval/summary_v7.json` (2026-07-03).

## Mode B under fixed hybrid

**Mode B holds.** The −0.125 regression measured against broken hybrid (0.419 baseline)
was **hybrid-specific collateral** from Jaccard RRF. Against literal-gated hybrid:

- Aggregate Mode B P@1: **0.500 → 0.500**
- `git-undo` queries: both remain P@1
- Rank shifts on `git-rebase` / `git-merge` / `db-migrate-down` cancel out at P@1

Excluding git sessions from enrichment pool is unchanged; the fix was gating hybrid,
not doc gating.

## Prior measurement (obsolete baseline)

Against broken hybrid (P@1 0.419), universal−git showed Mode B **0.125** — misleading.
Do not use `summary_v5.json` for Mode B decisions.

## Keyword-heavy slice

Enrichment shifts one literal query (`alembic upgrade head revision migrate`) from
rank 1→2; keyword-heavy P@1 **1.000 → 0.933**. Standard 86-query set unaffected.

## Recommendation

**Ready to merge** after `fix/hybrid-default` lands: Mode B holds, full set +0.012,
Mode C +0.050. Review keyword-heavy regression before release if that slice matters.

## Implementation

`whatwasit/models.py`: `_should_enrich_session()` — enrich all non-git workflows;
`_is_git_workflow_session()` skips sessions with ≥2 `git` commands.
