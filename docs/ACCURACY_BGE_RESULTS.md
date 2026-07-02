# BGE-small-en-v1.5 asymmetric embedder evaluation

Model: `BAAI/bge-small-en-v1.5` (384-dim ONNX, query prefix only).  
Baseline: `sentence-transformers/all-MiniLM-L6-v2` from `eval/summary.json`.

**Re-index required:** `model_name` meta is stamped on index; delete `index.usearch` and
re-run `whatwasit index` after switching models.

## Aggregate (86 answerable intent-paraphrase queries)

| Model | P@1 | P@3 | P@5 | MRR | nDCG@5 |
|---|---:|---:|---:|---:|---:|
| MiniLM (baseline) | **0.535** | 0.275 | 0.186 | **0.700** | **0.751** |
| BGE (asymmetric) | 0.465 | 0.240 | 0.156 | 0.613 | 0.638 |
| Δ (BGE − MiniLM) | **−0.070** | −0.035 | −0.030 | −0.087 | −0.113 |

BGE underperforms MiniLM on aggregate accuracy despite asymmetric query/passage encoding.

## Weak topics (git-rebase, env-path, git-merge)

| Topic | MiniLM P@1 | BGE P@1 | MiniLM MRR | BGE MRR |
|---|---:|---:|---:|---:|
| git-rebase | 0.00 | 0.00 | 0.267 | 0.183 |
| env-path | **0.50** | **0.00** | 0.750 | 0.044 |
| git-merge | 0.00 | 0.00 | 0.300 | 0.269 |

BGE does not lift the weakest semantic topics; **env-path regresses sharply** (P@1 0.50 → 0.00).

## Null-query threshold sweep (BGE scores)

BGE cosine scores sit much higher than MiniLM (null top-1 mean **0.54** vs 0.21;
answerable correct@1 mean **0.63** vs 0.42). The distributions overlap heavily.

| Threshold | Null FP rate | Answerable suppressed |
|---:|---:|---:|
| 0.40 | **100%** | 0% |
| 0.50 | 80% | 0% |
| 0.55 | 40% | 5% |
| **0.60** | **10%** | **20%** |

**Recommendation for TUI subagent:** `low_confidence_threshold = 0.40` is **not valid**
for BGE. If this model ships, use **~0.55–0.60** (compromise: **0.55** — 40% null FP,
5% good-query suppression). Do **not** hard-suppress results below threshold in v1.

`Config.low_confidence_threshold` remains `0.40` as the MiniLM-era default; override
when `model_name` is BGE or re-tune after any embedder change.

## Implementation notes

1. **Length penalty:** MiniLM-calibrated pivoted length normalization reorders BGE
   top-1 heavily (P@1 0.465 → 0.302). Search skips length penalty for asymmetric
   embedders (`encode_query` present).
2. **ONNX source:** `BAAI/bge-small-en-v1.5` with `onnx/model.onnx` + root
   `tokenizer.json` (Qdrant export repo unavailable).

## Merge recommendation

**Do not merge as default embedder.** Keep MiniLM or evaluate **e5-small-v2** next.
BGE regresses aggregate P@1 by 7 pp and fails to improve git-rebase / git-merge;
env-path is worse.

Artifacts: `eval/summary_bge.json`, `eval/summary_v2.json`, `eval/tables_v2.md`.
