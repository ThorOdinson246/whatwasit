"""Benchmark cold subprocess vs warm in-process query latency.

Run:  python benchmarks/query_cold_warm.py

Measures:
  - cold: subprocess ``python -m hist.cli <query>`` (fresh process each run)
  - warm: in-process ``search()`` reusing a loaded embedder

Also checks that cached cold runs do not emit Hugging Face progress bars.
"""

from __future__ import annotations

import argparse
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hist.config import Config
from hist.embedder import build_embedder, is_model_cached
from hist.search import search

DEFAULT_QUERY = "nginx config"
DEFAULT_RUNS = 5


def _has_hf_progress(stderr: str) -> bool:
    markers = ("Downloading", "Fetching", "100%|", "huggingface.co")
    return any(m in stderr for m in markers)


def bench_cold_subprocess(query: str, runs: int) -> dict:
    from hist.daemon import stop_daemon

    stop_daemon()  # measure true cold in-process load, not daemon RPC
    times: list[float] = []
    progress_hits = 0
    env = {**os.environ, "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
    for _ in range(runs):
        t0 = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, "-m", "hist.cli", query],
            capture_output=True,
            text=True,
            env=env,
        )
        elapsed = time.perf_counter() - t0
        times.append(elapsed)
        if _has_hf_progress(proc.stderr + proc.stdout):
            progress_hits += 1
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr or proc.stdout)

    return {
        "avg_ms": statistics.mean(times) * 1000,
        "min_ms": min(times) * 1000,
        "max_ms": max(times) * 1000,
        "progress_bar_runs": progress_hits,
    }


def bench_warm_inprocess(query: str, runs: int) -> dict:
    config = Config.default()
    embedder = build_embedder(config)
    embedder.encode(["warmup"])

    times: list[float] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        search(config, query, k=10, embedder=embedder)
        times.append(time.perf_counter() - t0)

    return {
        "avg_ms": statistics.mean(times) * 1000,
        "min_ms": min(times) * 1000,
        "max_ms": max(times) * 1000,
    }


def bench_daemon_subprocess(query: str, runs: int) -> dict:
    from hist.daemon import _wait_for_daemon, daemon_search, start_daemon, stop_daemon

    config = Config.default()
    stop_daemon()
    start_daemon(config)
    if not _wait_for_daemon(config):
        stop_daemon()
        raise RuntimeError("daemon failed to start")
    try:
        daemon_search(config, query, k=10)  # warmup RPC
        times: list[float] = []
        for _ in range(runs):
            t0 = time.perf_counter()
            results = daemon_search(config, query, k=10)
            if results is None:
                raise RuntimeError("daemon search unavailable")
            times.append(time.perf_counter() - t0)
    finally:
        stop_daemon(config)

    return {
        "avg_ms": statistics.mean(times) * 1000,
        "min_ms": min(times) * 1000,
        "max_ms": max(times) * 1000,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", default=DEFAULT_QUERY)
    ap.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    args = ap.parse_args()

    config = Config.default()
    cached = is_model_cached(config)
    print(f"model cached: {cached}")
    print(f"data_dir: {config.data_dir}")
    print(f"db exists: {config.db_path.exists()}")
    print()

    cold = bench_cold_subprocess(args.query, args.runs)
    warm = bench_warm_inprocess(args.query, args.runs)
    daemon = bench_daemon_subprocess(args.query, args.runs)

    print(f"{'mode':<12} {'avg':>10} {'min':>10} {'max':>10}")
    print(f"{'cold':<12} {cold['avg_ms']:>9.0f}ms {cold['min_ms']:>9.0f}ms {cold['max_ms']:>9.0f}ms")
    print(f"{'warm':<12} {warm['avg_ms']:>9.0f}ms {warm['min_ms']:>9.0f}ms {warm['max_ms']:>9.0f}ms")
    print(f"{'daemon':<12} {daemon['avg_ms']:>9.0f}ms {daemon['min_ms']:>9.0f}ms {daemon['max_ms']:>9.0f}ms")
    print()
    print(f"cold runs with HF progress output: {cold['progress_bar_runs']}/{args.runs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
