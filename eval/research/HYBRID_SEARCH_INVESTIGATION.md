# Hybrid search regression investigation (2026-07-03)

## Summary

Hybrid search (`config.hybrid_search=True`, shipping default) regresses P@1 by
**−0.116** vs semantic-only on the 86-query intent-paraphrase eval set:

| Path | P@1 | MRR | nDCG@5 |
|------|----:|----:|-------:|
| Semantic-only (`hybrid_search=False`) | **0.535** | 0.700 | 0.751 |
| Hybrid (shipping default) | **0.419** | 0.596 | 0.656 |

Deterministic (verified ×3 each). Root cause is **not** BM25/FTS on this eval set.

## What changed in git

| Commit | Effect |
|--------|--------|
| `927fad5` | `eval/summary.json` generated — semantic-only path (no hybrid) |
| `f1f08e2` | Hybrid search shipped: FTS leg + Jaccard RRF fusion, `hybrid_search=True` default |
| `fe2a235` | Eval artifacts updated to reflect hybrid-on baseline (0.419) |

The 0.535 number was never wrong for its era — it measured a **different search path**.

## The 22 rank-differing queries

**22/86** queries change rank between semantic-only and hybrid.

| Outcome | Count |
|---------|------:|
| Hybrid **hurts** (semantic had P@1, hybrid does not) | **11** |
| Hybrid **helps** (hybrid gained P@1) | **1** |
| Reordered but P@1 unchanged | 10 |

### Failure mode breakdown (11 hurt @ P@1)

| Category | Count | Mechanism |
|----------|------:|-----------|
| **Distractor promoted** | **10** | Jaccard keyword leg + RRF elevates `distractor_*` over correct labeled session |
| **Undo/rollback family** | **1** | `git_undo_commit` → `db_migration_rollback` (semantic sibling swap via RRF) |

Examples of distractor promotion (semantic P@1 → hybrid miss):

| Query topic | Sem top-1 | Hybrid top-1 | Sem rank → Hyb rank |
|-------------|-----------|--------------|---------------------|
| cron-setup | `cron_job_setup` | `distractor_02` | 1 → 7 |
| tar-archive | `tar_backup` | `distractor_06` | 1 → 5 |
| rsync-sync | `rsync_transfer` | `distractor_06` | 1 → 11 |
| gpg-encrypt | `gpg_encrypt_file` | `distractor_03` | 1 → 5 |
| sed-replace | `find_replace_sed` | `distractor_13` | 1 → 5 |

## RRF / BM25 / tokenization analysis

### Hybrid activation (27/86 queries)

| Leg | Queries activated |
|-----|------------------:|
| FTS5 BM25 (`sessions_fts`) | **0** |
| Jaccard `_keyword_score` on semantic candidates | **27** |

On intent-paraphrase queries, the hybrid gate opens because `max_kw >= 0.08`
(Jaccard overlap between NL query tokens and `doc_text`), **not** because FTS
returns hits. `build_fts_match_query()` uses AND of quoted tokens — intent queries
rarely match terse command docs via FTS5.

**Conclusion:** BM25 tokenization is **not** the noise source on this eval set.
The regression is almost entirely from **Jaccard RRF fusion** over semantic top-k.

### Why Jaccard hurts

1. **`_keyword_score`** is Jaccard overlap between query tokens and `doc_text`
   (commands + `directory:` + `context:` hints), stripped of only the `context:`
   line prefix — not commands.

2. **Long distractor sessions** (7+ commands, public-dataset text) have large
   token bags → higher Jaccard overlap with generic NL query words ("directory",
   "file", "system", "script", etc.) than short labeled targets.

3. **RRF (`k=60`)** merges semantic rank with Jaccard rank with equal weight.
   A distractor at Jaccard rank 1 can outscore the semantically correct session
   at semantic rank 2–3.

4. **`_HYBRID_KW_MIN_SCORE = 0.08`** is low enough to activate on most queries
   where semantic retrieval already found keyword-overlapping candidates.

### FTS / BM25 details (for when it does fire)

- Index: `sessions_fts` FTS5, `tokenize='unicode61'`
- Indexed field: full `doc_text` (directory line + commands + context hints)
- BM25 scores negated to higher-is-better
- Used on literal/short queries via fast path; not implicated in the 11 P@1 losses

## Recommendation

**Do not ship hybrid as default until the Jaccard leg is fixed or gated.**

**Resolved:** literal gate shipped in `fix/hybrid-default` — see
[HYBRID_LITERAL_GATE.md](HYBRID_LITERAL_GATE.md).

| Option | Tradeoff |
|--------|----------|
| **A. Default `hybrid_search=False`** | Restores P@1 0.535 immediately; loses hybrid gains on literal queries (keyword-heavy slice still P@1 1.0 semantic-only) |
| **B. Gate hybrid to literal queries only** | `looks_literal_query()` already exists; extend so RRF runs only there |
| **C. Replace Jaccard with FTS-only leg** | FTS didn't fire on intent queries — may be safe but needs re-eval |
| **D. Raise `_HYBRID_KW_MIN_SCORE` or require FTS hit** | May stop spurious activation; tune on eval |

**Recommended near-term:** **Option A or B** — semantic-only as default for NL intent
queries matches eval evidence. Hybrid value is on keyword/literal paths; the current
gate activates hybrid on intent queries and promotes distractors.

## Reproduce

```bash
# Compare paths on main (pure models.py)
python3 -c "
# ... see eval/research/BASELINE_REPRO.md
"
```

Or toggle in eval harness: `config.hybrid_search = False` vs `True`.
