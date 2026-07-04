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

**Reproduced 2026-07-03** on `main`.

**Standard set (86 answerable queries)**

| Method | P@1 | MRR | nDCG@5 | Notes |
|--------|-----|-----|--------|-------|
| semantic (**shipping**) | **0.547** | 0.701 | 0.746 | literal-gated hybrid + universal doc enrichment |
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
python eval/build_dataset.py standard

# Run the historical default: standard + keyword-heavy breakout.
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python eval/run_eval.py

# Run one suite explicitly.
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python eval/run_eval.py --suite standard --retrieval-k full
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python eval/run_eval.py --suite hard --retrieval-k production

# Run every available suite separately.
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python eval/run_eval.py --all-suites --retrieval-k production

# Copy versioned output to canonical files if updating the checked-in baseline:
# cp eval/summary_vN.json eval/summary.json
# cp eval/tables_vN.md eval/tables.md
# cp eval/metrics_summary_vN.csv eval/metrics_summary.csv
```

The harness indexes all sessions through the real whatwasit pipeline, runs both
semantic search and a keyword/fuzzy baseline, and computes standard IR metrics
(P@k, R@k, MRR, nDCG@k). Summary JSON includes `search_config`.

## Eval suites

The runner supports named suites:

| Suite | Purpose |
|---|---|
| `standard` | Canonical intent-paraphrase baseline (`sessions.jsonl`, `queries.jsonl`) |
| `keyword_heavy` | Literal/tool/flag breakout over the standard corpus |
| `hard` | Confusable/noisy/error/path/null promotion gate |
| `raw_noise` | Optional external raw-command stress suite when generated locally |

`--retrieval-k full` is diagnostic and ranks as deeply as the suite corpus allows.
`--retrieval-k production` uses `Config.top_k` (currently 10) and records the
effective cap in summary metadata. Do not compare full-depth and production-top-k
runs as equivalent.

## External raw data

Raw public datasets should stay outside git under `eval/external_raw/` or
`eval/raw_downloads/`. To convert line-based command samples into deterministic
synthetic sessions:

```bash
python eval/build_dataset.py raw \
  --input eval/raw_sources/*.txt \
  --suite raw_noise \
  --source bundled_raw \
  --session-size 5 \
  --limit 500
```

Generated `raw_*` files are ignored by default. Commit only deliberately curated
samples and provenance.

## Comparing runs

Use `eval.compare` to compare two summary files:

```bash
python -m eval.compare eval/summary_old.json eval/summary_new.json
```

The comparison report includes aggregate metric deltas, answerable rank
movements, null top-score changes, and timing mean deltas.
