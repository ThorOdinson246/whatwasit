# BGE benchmark comparison (vs MiniLM baseline)

Measured on the eval machine (offline, `benchmarks/run_bench.py`).  
MiniLM reference: `BENCHMARKS.md` “Confirmed on un-throttled hardware” (i9-14900).

## Indexing and query latency

| Commands | Sessions | BGE index | BGE q-avg | MiniLM index | MiniLM q-avg |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 109 | 3.38 s | 387.7 ms | 0.80 s | 65.1 ms |
| 10,000 | 1,087 | **37.72 s** | 357.8 ms | **7.19 s** | 165.0 ms |
| 100,000 | 10,870 | 508.06 s | 712.8 ms | 92.89 s | 153.3 ms |

Pure ANN search over 100k vectors: **1.5 ms avg** (MiniLM: 0.7 ms).

## Requirement checks (BGE)

| Requirement | Result | Margin |
|---|---|---|
| HR#3 — index 10k commands < 30 s | **FAIL** (37.72 s) | −26% over budget |
| HR#5 — query < 1 s at 100k sessions | **PASS** (712.8 ms avg) | ~1.4× headroom |

BGE is ~5× slower than MiniLM on indexing and ~2–4× slower on full query path,
but still clears the query latency budget at 100k. Indexing at 10k exceeds HR#3 on
this hardware (would need ~22% faster encode or a faster CPU to pass).

## Notes

- Query latency is dominated by two ONNX forward passes (query + command batch), not ANN.
- Expect ~1.3–1.5× encode slowdown vs MiniLM from 12-layer vs 6-layer transformer;
  observed gap is larger, likely machine/thermal variance between runs.
