# Accuracy Research (proposals only)

Workstream C deliverable for the `docs/accuracy-research` branch. **No production
code changes** — this document records research and UX proposals for improving
search accuracy and user trust.

**Current baseline:** `sentence-transformers/all-MiniLM-L6-v2` (384-dim, symmetric)
via `OnnxEmbedder` → P@1 **0.535** on 86 intent-paraphrase queries (`eval/README.md`).

---

## C1 — Embedding model shortlist

### Why swap is low-risk

The `Embedder` ABC (`whatwasit/interfaces.py`) requires only `dim` and
`encode(texts) -> (n, dim)` with L2-normalized rows. `OnnxEmbedder`
(`whatwasit/embedder.py`) already parameterizes `model_name`, `dim`, and `onnx_repo`
via `_ONNX_REPOS`; swapping models is a one-class change plus config + full
re-index. Indexer, search, and CLI stay untouched.

**Re-index is mandatory for any model change.** Vectors live in incompatible
semantic spaces even when dimension matches (384). Plan: bump a `model_name` meta
field, delete `index.usearch`, re-run `whatwasit index`.

### Comparison table

| Model | Dim | Params | ONNX size (FP32) | CPU speed (est.) | Symmetry | NL query → shell commands |
|---|---:|---:|---:|---:|---|---|
| **all-MiniLM-L6-v2** *(current)* | 384 | 22 M | ~90 MB | **~600 texts/s** (measured, i9-14900) | Symmetric | Adequate MVP; conflates undo/rebase/rollback sessions |
| **intfloat/e5-small-v2** | 384 | 33 M | ~130 MB | ~400–500 texts/s | **Asymmetric** — `query:` / `passage:` prefixes | Designed for retrieval; prefixes map cleanly to NL queries vs command docs |
| **BAAI/bge-small-en-v1.5** | 384 | 33 M | ~133 MB | ~400–500 texts/s | **Asymmetric** — instruction prefix on queries only | Top MTEB small-model retrieval; passage = raw session doc |
| **thenlper/gte-small** | 384 | 33 M | ~133 MB | ~400–500 texts/s | Mostly symmetric (optional query prefix) | Strong general embeddings; less retrieval-specific than e5/bge |

Speed estimates assume the same `onnxruntime` pipeline (ORT_ENABLE_ALL,
`intra_op_num_threads = cpu_count`, batch 256). The three candidates have 12
transformer layers vs MiniLM's 6, so expect **~1.3–1.5× slower** encode while
still clearing HR#3/HR#5 with margin (query latency is dominated by two small
encode passes, not ANN search — see `BENCHMARKS.md`).

### ONNX availability

| Model | Ready-made ONNX repo | Notes |
|---|---|---|
| MiniLM-L6-v2 | `qdrant/all-MiniLM-L6-v2-onnx` | Shipping today (`_ONNX_REPOS`) |
| e5-small-v2 | FastEmbed / Qdrant ecosystem (`intfloat/e5-small-v2` in fastembed registry) | No official ONNX under `intfloat/e5-small-v2`; use Qdrant-exported weights or one-time `optimum` export. Pooling: mean + L2 norm. |
| bge-small-en-v1.5 | `BAAI/bge-small-en-v1.5/onnx/model.onnx` or `Qdrant/bge-small-en-v1.5-onnx` | Verified public ONNX (~133 MB). |
| gte-small | `Qdrant/gte-small-onnx` | Verified public ONNX (~133 MB). |

All candidates fit the existing `OnnxEmbedder` shape: `tokenizer.json` +
`model.onnx`, mean pooling over last hidden state, L2 normalize. Asymmetric
models need prefix injection in `encode()` — either a `mode="query"|"passage"`
parameter or separate `encode_query` / `encode_passage` methods on a subclass.

### Prefix conventions (for asymmetric evaluation)

```
# e5-small-v2
query:   "query: {user text}"
passage: "passage: {session.to_document()}"

# bge-small-en-v1.5
query:   "Represent this sentence for searching relevant passages: {user text}"
passage: "{session.to_document()}"   # no prefix

# gte-small (optional asymmetric)
query:   "query: {user text}"          # try with and without
passage: "{session.to_document()}"
```

Session documents should continue to use `Session.to_document()` (commands +
`directory:` line + `context:` hints). Prefixes apply at encode time, not in
stored `doc_text`.

### Recommendation: evaluate **BAAI/bge-small-en-v1.5** first

1. **Best retrieval fit** among 384-dim small models on MTEB retrieval tasks.
2. **Explicit asymmetric encoding** matches whatwasit's core mismatch: natural-language
   queries vs terse shell commands.
3. **Same 384 dimensions** — no `usearch` index rebuild for dimension change,
   only vector replacement.
4. **Public ONNX** ready on Hugging Face (`BAAI/.../onnx/`).

**Second:** `intfloat/e5-small-v2` — simpler, well-standardized `query:`/`passage:`
prefixes; benchmark if bge doesn't lift git-rebase / env-path style failures.

**Third:** `thenlper/gte-small` — symmetric baseline to quantify how much
asymmetry alone buys us.

### Evaluation plan

1. Add `AsymmetricOnnxEmbedder` behind `Embedder` ABC (separate PR).
2. Re-index eval corpus; re-run `eval/run_eval.py`.
3. Track per-topic deltas for `git-rebase`, `env-path`, `git-merge` (weakest
   semantic topics in `eval/tables.md`).
4. Re-benchmark encode throughput on target hardware before merging.

---

## C2 — Low-confidence UX proposal (future TUI)

**Scope:** UX design only. Do not implement in this branch.

### Observed failure modes (real user testing)

| Query intent | Top-1 score | Top-1 result | Correct session | Problem |
|---|---:|---|---|---|
| CUDA / GPU fix | **0.28** | unrelated | *(none)* | True negative — low score correctly signals weak match |
| Git interactive rebase | **0.68** | `git_undo_commit` (wrong) | `git_rebase_conflict` at **#10** | High-confidence false positive; user trusts wrong session |
| Shell PATH / environment | **0.66** | unrelated | `env_var_debug` (`vim ~/.bashrc`) at **#10** | Same pattern — plausible score, wrong session |

Eval harness confirms the pattern: null-query top-1 scores cluster at
mean **0.21** (max 0.40), while answerable correct@1 scores mean **0.42**
(`eval/summary.json` → `null_analysis`). The rebase and env-path cases sit
*above* the null distribution — raw score alone cannot distinguish them from
good matches.

### Proposed threshold: **~0.40**

Derived from eval threshold sweep (`eval/run_eval.py`):

| Threshold | Null FP rate (showing a "match" when none exists) | Answerable suppressed (hiding good results) |
|---:|---:|---:|
| 0.30 | 10% | 11% |
| 0.35 | 10% | 24% |
| **0.40** | **10%** | **46%** |
| 0.45 | 0% | 70% |

**0.40 is a compromise anchor**, not a silver bullet:

- **Global empty-state:** If top-1 score `< 0.40`, show a banner:
  `No confident matches for this query — results below may not be relevant.`
  Correctly handles the CUDA case (0.28).
- **Does not fix** 0.66–0.68 false positives. Those need complementary signals
  (see badges below).

Do **not** hard-suppress results below 0.40 in v1 — too many good answerable
queries have top-1 scores in the 0.35–0.45 band (eval P@1 would collapse).

### TUI banner (top of results)

```
┌─ whatwasit ─────────────────────────────────────────────────────────────┐
│  Query: "redo my branch history one commit at a time"                │
│  ⚠ Low confidence — top match score 0.68; verify before re-running.  │
└────────────────────────────────────────────────────────────────────┘
```

Show when **any** of:

- `top1_score < 0.40` (no confident match), or
- `top1_score ≥ 0.40` **and** `correct_session_rank > 3` *(offline eval only;
  production proxy: top1–top2 margin < 0.05 **and** keyword Jaccard < 0.08)*, or
- `top1_score ≥ 0.40` **and** `keyword_overlap(top1) == 0` for queries with
  ≥ 3 content tokens

### Per-result badges

| Badge | Condition | Meaning |
|---|---|---|
| `● match` | score ≥ 0.50 **and** (rank 1 with margin ≥ 0.08 over #2) | Strong semantic match |
| `◐ maybe` | 0.35 ≤ score < 0.50, or #1 with margin < 0.08 | Plausible but verify |
| `○ weak` | score < 0.35 | Unlikely relevant |

For the git-rebase case (0.68, margin over #2 ~0.09): badge `◐ maybe` because
keyword overlap with `rebase` is 0 — triggers the combined rule even when score
looks high.

### Plain mode (`whatwasit search --plain` / scripting)

Prefix uncertain lines so scripts can filter:

```
[?] 0.68  2025-03-14  ~/projects/api
      > git revert HEAD~1          ← wrong session highlighted
        git log --oneline -5
```

Rules:

- `[?]` when badge would be `◐ maybe` or `○ weak`
- No prefix when `● match`
- If **all** results are `○ weak`, print banner text to stderr:
  `whatwasit: no confident matches (best score 0.28)`

### Why score-only thresholds are insufficient

High-score wrong answers (0.66–0.68) are structurally similar sessions: git
undo, migration rollback, and rebase all look like "fixing project history" to
a symmetric embedder. The UX must communicate **verify, don't trust** without
hiding potentially correct results at rank 10.

---

## C3 — "Feels like magic" opportunities

Ranked by **impact ÷ effort** for a local-first shell-history search tool.
Impact = accuracy or perceived accuracy; effort = engineering time + re-index
cost.

| Rank | Opportunity | Effort | Impact | Notes |
|:---:|---|---|---|---|
| 1 | **Matched-command focus in TUI** | Low | High | Today `output.py` shows full session with `>` on matched commands. Promote the top matched command to the panel header (one line, copyable). Users care about the *command*, not the session wrapper. |
| 2 | **Keyword boost for query tokens** | Low | Medium–High | Hybrid RRF exists but is **gated at `_HYBRID_KW_MIN_SCORE = 0.20`** (`whatwasit/search.py`). Intent-paraphrase queries score Jaccard **< 0.04** on all candidates, so hybrid **never fires** for the queries that need it most. Lower gate to ~0.05 for token overlap on *any* query token appearing in raw commands, or add a lightweight BM25 pre-filter. |
| 3 | **Recency tie-break** | Low | Low–Medium | When semantic scores are within 0.05, prefer newer `start_ts`. Cheap, no re-index. Helps "that thing I did last week" disambiguation. |
| 4 | **fzf re-filter on results** | Medium | High | Listed in `FUTURE_IDEAS.md`. Interactive narrowing of top-20 semantic results. High perceived magic; medium effort (TUI dependency). |
| 5 | **Asymmetric embedder (bge/e5)** | Medium | High | See C1. One-class swap + full re-index. Targets the NL→command gap directly. |
| 6 | **Per-command vector index** | High | High | `FUTURE_IDEAS.md`. Embed each command, not just session aggregate. Fixes "correct command buried in noisy session" but multiplies index size and index time. |
| 7 | **Live incremental index** | Very high | High (long-term) | Daemon + hooks. Not an accuracy fix per se, but removes stale-index frustration. |

### Hybrid search dead zone (why keyword boost matters)

```
Intent query tokens:     "redo branch history one commit at a time"
Session raw commands:    git fetch; git rebase origin/main; vim ...; git rebase --continue
Jaccard after hint-strip: ~0.02–0.06   ← below 0.20 gate
Hybrid RRF:              SKIPPED → pure semantic ranking
```

Keyword-heavy queries (exact tool names) already score P@1 **1.00** semantic
(`eval/README.md` keyword-heavy breakout). The gap is **intent paraphrases**
where a single token (`rebase`, `bashrc`, `PATH`) would rerank correctly but
the 0.20 gate prevents it.

**Quick win proposal:** add a *soft* keyword signal (not gated) as a tie-breaker:
`final_score = semantic_score + 0.05 * jaccard(query, raw_commands)` when
`jaccard > 0`. No RRF, no calibration, re-index not required.

### Suggested implementation order

1. Matched-command focus + recency tie-break (no re-index, ship in TUI PR)
2. Soft keyword tie-break (search.py only)
3. Asymmetric embedder eval (bge-small-en-v1.5)
4. fzf interactive mode
5. Per-command index (if session-level ceiling is hit)

---

## References

- `whatwasit/embedder.py` — `OnnxEmbedder`, `_ONNX_REPOS`, `build_embedder()`
- `whatwasit/interfaces.py` — `Embedder` ABC
- `whatwasit/search.py` — hybrid RRF, `_HYBRID_KW_MIN_SCORE`, `_rank_matches()`
- `whatwasit/models.py` — `Session.to_document()`, `_COMMAND_HINTS`
- `eval/README.md`, `eval/summary.json`, `eval/tables.md` — baseline metrics
- `BENCHMARKS.md` — encode throughput and latency budgets
- `FUTURE_IDEAS.md` — asymmetric models, per-command index, fzf mode
