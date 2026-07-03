# Eval research notes

Investigation write-ups for search-quality regressions and fixes on the
intent-paraphrase eval set (`eval/queries.jsonl`, 86 answerable queries).

| Document | Topic |
|----------|-------|
| [BASELINE_REPRO.md](BASELINE_REPRO.md) | Why committed `summary.json` showed P@1 0.535 while shipping hybrid measured 0.419 |
| [HYBRID_SEARCH_INVESTIGATION.md](HYBRID_SEARCH_INVESTIGATION.md) | Root-cause analysis: Jaccard RRF promoted distractors on intent queries |
| [HYBRID_LITERAL_GATE.md](HYBRID_LITERAL_GATE.md) | Fix: gate hybrid RRF to `looks_literal_query()` only; restores P@1 0.535 |
| [RICHER_SESSION_DOCS.md](RICHER_SESSION_DOCS.md) | Universal doc enrichment (git sessions excluded); +0.012 P@1 on gated baseline |

Chronology: stale baseline → broken-hybrid diagnosis → literal gate → enrichment re-measure.
