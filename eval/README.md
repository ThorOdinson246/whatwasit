# Search quality evaluation

Offline evaluation harness for measuring how well `whatwasit` retrieves the right
shell-history session from a natural-language query.

## Dataset

| File | Description |
|------|-------------|
| `sessions.jsonl` | 57 sessions (43 labeled topics + 14 distractors from public command datasets) |
| `queries.jsonl` | 86 answerable intent-paraphrase queries + 10 null queries |
| `queries_keyword_heavy.jsonl` | 15 keyword-heavy queries (exact tool names / flags) — reported separately |

Queries are written to test **intent recall**, not keyword luck: answerable
queries deliberately avoid reusing the literal command words of their target
session.

## Latest results

Measured with `python eval/run_eval.py` against `whatwasit.search.search()` on
**`main`** (MiniLM, length normalization, universal session doc enrichment,
literal-gated hybrid). The harness uses production defaults
(`Config.hybrid_search=True`); hybrid RRF/FTS fusion runs only for **literal
queries** (`looks_literal_query()`).

**Reproduced 2026-07-03** — investigation write-ups:
[`eval/research/README.md`](research/README.md).

**Standard set (86 answerable queries)**

| Method | P@1 | MRR | nDCG@5 | Notes |
|--------|-----|-----|--------|-------|
| semantic (**shipping**) | **0.547** | 0.701 | 0.746 | literal-gated hybrid + universal doc enrichment |
| semantic (gated hybrid, no enrichment) | 0.535 | 0.700 | 0.751 | hybrid fix only |
| semantic (broken hybrid, pre-fix) | 0.419 | 0.596 | 0.656 | Jaccard RRF on all queries |
| keyword baseline | 0.372 | 0.488 | 0.492 | eval fuzzy ranker |

**Keyword-heavy breakout (15 queries)**

| Method | P@1 | MRR | nDCG@5 |
|--------|-----|-----|--------|
| semantic (whatwasit) | 0.933 | 0.967 | 0.975 |
| keyword baseline | 0.933 | 0.967 | 0.975 |

Known tradeoff: enrichment shifts the `alembic upgrade head revision migrate`
literal query from P@1 1.000 → 0.933 (accepted; standard 86-query set unaffected).

Full per-query breakdown: [`tables.md`](tables.md). Raw numbers:
[`summary.json`](summary.json), [`metrics_summary.csv`](metrics_summary.csv).

## Reproduce

```bash
# Regenerate the labeled dataset (optional; requires pyarrow for parquet sources)
python eval/build_dataset.py

# Run evaluation (writes versioned artifacts; takes ~5 min on CPU)
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python eval/run_eval.py

# Copy versioned output to canonical files if updating the checked-in baseline:
# cp eval/summary_vN.json eval/summary.json
# cp eval/tables_vN.md eval/tables.md
# cp eval/metrics_summary_vN.csv eval/metrics_summary.csv
```

The harness indexes all sessions through the real whatwasit pipeline, runs both
semantic search and a keyword/fuzzy baseline, and computes standard IR metrics
(P@k, R@k, MRR, nDCG@k). Summary JSON includes `search_config`.
