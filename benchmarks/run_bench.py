"""Benchmark hist indexing and query latency at 1k / 10k / 100k scale.

Run:  python benchmarks/run_bench.py [--write-md]

Measures, for each command-count scale:
  - indexing time (parse-free: synthetic Commands -> group -> embed -> store)
  - resulting session count
  - query latency (query encode + nearest-neighbour search), averaged

Also runs a pure approximate-nearest-neighbour search benchmark over 100k+
session vectors to validate the <1s query-latency requirement at that scale.

Uses the real local MiniLM model from cache, fully offline.
"""

from __future__ import annotations

import argparse
import os
import statistics
import sys
import tempfile
import time
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

# Allow running directly from the repo without installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from hist.config import Config
from hist.embedder import build_embedder
from hist.index import UsearchIndex, build_index
from hist.indexer import index_commands
from hist.search import search
from tests import synthetic

SCALES = [1_000, 10_000, 100_000]
QUERIES = list(synthetic.TOPIC_QUERIES.values())


def _fmt(seconds: float) -> str:
    if seconds < 1:
        return f"{seconds * 1000:.1f} ms"
    return f"{seconds:.2f} s"


def bench_scale(n: int, embedder) -> dict:
    commands = synthetic.generate_commands(n, seed=1)
    tmp = tempfile.mkdtemp(prefix=f"histbench_{n}_")
    config = Config(data_dir=Path(tmp))
    index = build_index(config)

    t0 = time.perf_counter()
    stats = index_commands(config, commands, embedder=embedder, index=index, reset=True)
    index_elapsed = time.perf_counter() - t0

    # Query latency: encode query + search, averaged over the topic queries.
    # Warm up once (model already loaded, but warms the search path).
    search(config, QUERIES[0], k=10, embedder=embedder)
    latencies = []
    for q in QUERIES:
        t0 = time.perf_counter()
        search(config, q, k=10, embedder=embedder)
        latencies.append(time.perf_counter() - t0)

    return {
        "n_commands": n,
        "n_sessions": stats.n_sessions,
        "index_elapsed": index_elapsed,
        "query_avg": statistics.mean(latencies),
        "query_max": max(latencies),
    }


def bench_pure_ann(n_sessions: int, embedder, dim: int = 384) -> dict:
    """Pure ANN search latency over n_sessions random vectors (no DB hydration)."""
    rng = np.random.default_rng(0)
    vecs = rng.standard_normal((n_sessions, dim)).astype(np.float32)
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    keys = np.arange(n_sessions, dtype=np.int64)

    tmp = tempfile.mkdtemp(prefix="histann_")
    idx = UsearchIndex(Path(tmp) / "index.usearch", dim=dim)
    t0 = time.perf_counter()
    idx.add(keys, vecs)
    build_elapsed = time.perf_counter() - t0

    qvecs = embedder.encode(QUERIES)
    latencies = []
    for qv in qvecs:
        t0 = time.perf_counter()
        idx.search(qv, 10)
        latencies.append(time.perf_counter() - t0)

    return {
        "n_sessions": n_sessions,
        "build_elapsed": build_elapsed,
        "search_avg": statistics.mean(latencies),
        "search_max": max(latencies),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-md", action="store_true", help="write BENCHMARKS.md")
    args = ap.parse_args()

    embedder = build_embedder(Config())
    embedder.encode(["warmup"])  # load model once, excluded from timings

    print(f"{'commands':>10} {'sessions':>9} {'index':>10} {'q-avg':>10} {'q-max':>10}", flush=True)
    rows = []
    for n in SCALES:
        r = bench_scale(n, embedder)
        rows.append(r)
        print(
            f"{r['n_commands']:>10} {r['n_sessions']:>9} "
            f"{_fmt(r['index_elapsed']):>10} {_fmt(r['query_avg']):>10} "
            f"{_fmt(r['query_max']):>10}",
            flush=True,
        )

    ann = bench_pure_ann(100_000, embedder)
    print(
        f"\nPure ANN over {ann['n_sessions']} session vectors: "
        f"avg search {_fmt(ann['search_avg'])}, max {_fmt(ann['search_max'])}",
        flush=True,
    )

    if args.write_md:
        _write_md(rows, ann)
        print("\nwrote BENCHMARKS.md")
    return 0


def _write_md(rows, ann) -> None:
    import platform

    cpu = platform.processor() or platform.machine()
    md = []
    md.append("# Benchmarks\n")
    md.append(
        "Measured on a laptop CPU (no GPU), fully offline, embedding model "
        "`all-MiniLM-L6-v2` (384-dim int8 ONNX via fastembed), vector store "
        "`usearch`.\n"
    )
    md.append(f"- Machine: `{cpu}`, Python `{platform.python_version()}`, "
              f"{os.cpu_count()} logical CPUs\n")
    md.append("\n## Indexing and query latency by command count\n")
    md.append("Synthetic shell history is grouped into sessions, each session is "
              "embedded, and vectors are stored. Query latency = embed the query + "
              "nearest-neighbour search + hydrate results, averaged over the topic "
              "queries.\n")
    md.append("\n| Commands | Sessions | Index time | Query latency (avg) | Query latency (max) |")
    md.append("\n|---:|---:|---:|---:|---:|\n")
    for r in rows:
        md.append(
            f"| {r['n_commands']:,} | {r['n_sessions']:,} | {_fmt(r['index_elapsed'])} "
            f"| {_fmt(r['query_avg'])} | {_fmt(r['query_max'])} |\n"
        )
    md.append("\n## Pure nearest-neighbour search at scale\n")
    md.append(
        f"To validate the requirement of sub-second query at 100k+ indexed "
        f"sessions, search latency over **{ann['n_sessions']:,}** random session "
        f"vectors (384-dim):\n"
    )
    md.append(f"\n- Average search: **{_fmt(ann['search_avg'])}**")
    md.append(f"\n- Max search: **{_fmt(ann['search_max'])}**")
    md.append(f"\n- Index build (add {ann['n_sessions']:,} vectors): {_fmt(ann['build_elapsed'])}\n")
    md.append("\n## Requirement check\n")
    idx10k = next(r for r in rows if r["n_commands"] == 10_000)
    md.append(
        f"\n- HR#3 index 10k commands < 30s: **{_fmt(idx10k['index_elapsed'])}** "
        f"({'PASS' if idx10k['index_elapsed'] < 30 else 'FAIL'})"
    )
    md.append(
        f"\n- HR#5 query < 1s at 100k+ sessions: pure-ANN avg "
        f"**{_fmt(ann['search_avg'])}** "
        f"({'PASS' if ann['search_avg'] < 1 else 'FAIL'}); full query path at "
        f"largest scale avg **{_fmt(rows[-1]['query_avg'])}** "
        f"({'PASS' if rows[-1]['query_avg'] < 1 else 'FAIL'})\n"
    )
    Path(__file__).resolve().parents[1].joinpath("BENCHMARKS.md").write_text("".join(md))


if __name__ == "__main__":
    raise SystemExit(main())
