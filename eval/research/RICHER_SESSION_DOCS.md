# Richer session documents — Mode C fix (re-measured)

**Branch:** `feature/richer-session-docs`  
**Baseline:** `fix/eval-baseline-repro` — hybrid shipping path P@1 **0.419**  
(see `eval/research/BASELINE_REPRO.md` on that branch)

## Mode C gold sessions (10 / 20 queries)

`python_venv_setup`, `env_var_debug`, `python_profiling`, `python_dependency_conflict`,
`find_large_old_files`, `cron_job_setup`, `nginx_reverse_proxy`, `docker_volume_mount`,
`docker_disk_prune`, `git_large_file_purge`

## Eval artifacts

| Variant | File | P@1 full | P@1 Mode C | P@1 Mode B |
|---------|------|---------:|-----------:|-----------:|
| **Baseline** (main, hybrid on) | `fix/eval-baseline-repro:eval/summary.json` | 0.419 | 0.150 | 0.250 |
| **Sparse-only** enrichment | `eval/summary_sparse_enrichment.json` | **0.442** | 0.200 | 0.125 |
| **Universal** enrichment | `eval/summary_universal_enrichment.json` | **0.453** | **0.250** | 0.125 |

Δ vs baseline:

| Variant | Full Δ | Mode C Δ | Mode B Δ |
|---------|-------:|---------:|---------:|
| Sparse-only | +0.023 | +0.050 | **−0.125** |
| Universal | +0.035 | **+0.100** | **−0.125** |

Reproduced 2026-07-03; deterministic (single run each; baseline verified ×3).

## Cross-contamination: why enriching venv docs shifts git-rebase ranks

This is **not** a bug in reranking code — it follows from how the index works:

1. **Single shared embedding space.** All sessions are embedded into one 384-dim index.
   Changing `python_venv_setup`'s document changes its vector; cosine scores shift for
   **every** query against **every** session.

2. **Generic hint tokens overlap.** Enrichment adds phrases like "python virtual
   environment", "install python packages", "shell PATH environment". These are
   semantically close to many intent-paraphrase queries (including git undo/rebase
   phrased as "walking back changes" or "redoing history") and to distractor sessions
   that also received enrichment.

3. **Hybrid RRF couples FTS.** `doc_text` is stored in SQLite for FTS5. Enrichment
   changes BM25 ranks too; RRF merges semantic + keyword legs — a boost to unrelated
   sessions can reorder git siblings without any git session being edited.

4. **Length normalization.** Longer enriched docs get a smaller length penalty in the
   semantic leg, further boosting enriched sessions in the shared ranking.

**Observed Mode B collateral (baseline → sparse):** git-undo lost one P@1 hit
(rank 1→2) while git-rebase improved slightly (5→4) on one query — net Mode B P@1
down because undo/db hits were more valuable than rebase gains.

## Recommendation

**Do not merge either variant yet** — both regress Mode B (−0.125 P@1).

If forced to choose for further iteration: **universal enrichment** is the better
accuracy tradeoff (+0.035 full, +0.100 Mode C) with the **same** Mode B cost as
sparse-only. Prefer universal only if Mode B regression is accepted or fixed separately
(e.g. hybrid tuning, domain-tuned embedder, or query-conditioned gating).

Next steps before merge: fix hybrid regression on intent set, or decouple enrichment
from global index (e.g. re-embed only targeted sessions in A/B — not possible in
production without full re-index anyway).

## Implementation (sparse-only on branch)

Pattern-gated enrichment in `whatwasit/models.py` — see commit `c4c73f8`. Universal
numbers above used a local eval-only override of `_is_sparse_session()` (not committed).
