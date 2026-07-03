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
**unmodified `main`** (MiniLM, length normalization, session doc hints). The harness
uses production defaults (`Config.hybrid_search=True`).

**Reproduced 2026-07-03** — see [`eval/research/BASELINE_REPRO.md`](research/BASELINE_REPRO.md)
for why older docs showed P@1 0.535.

**Standard set (86 answerable queries)**

| Method | P@1 | MRR | nDCG@5 | Notes |
|--------|-----|-----|--------|-------|
| semantic (**shipping**, hybrid on) | **0.419** | 0.596 | 0.656 | current production path |
| semantic (hybrid off) | 0.535 | 0.700 | 0.751 | semantic-only reference |
| keyword baseline | 0.291 | 0.415 | 0.427 | eval fuzzy ranker |

**Keyword-heavy breakout (15 queries)**

| Method | P@1 | MRR | nDCG@5 |
|--------|-----|-----|--------|
| semantic (whatwasit) | 1.000 | 1.000 | 1.000 |
| keyword baseline | 0.933 | 0.967 | 0.975 |

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
(P@k, R@k, MRR, nDCG@k). Summary JSON includes `search_config.hybrid_search`.
