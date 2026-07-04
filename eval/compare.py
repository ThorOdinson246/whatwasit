"""Compare two eval summary JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

from eval import metrics


def load_summary(path: Path | str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def suites(summary: dict) -> dict[str, dict]:
    if "suites" in summary:
        return summary["suites"]
    out = {"standard": summary}
    if "keyword_heavy" in summary:
        kh = dict(summary["keyword_heavy"])
        kh.setdefault("null_analysis", {"details": []})
        kh.setdefault("timing", {})
        out["keyword_heavy"] = kh
    return out


def _rank_map(summary: dict) -> dict[str, int | None]:
    out: dict[str, int | None] = {}
    for row in summary.get("per_query", []):
        if row.get("gold") is None:
            continue
        key = row.get("query_id") or row["query"]
        out[key] = row["semantic"]["rank"]
    return out


def _null_scores(summary: dict) -> dict[str, float]:
    out: dict[str, float] = {}
    for row in summary.get("null_analysis", {}).get("details", []):
        key = row.get("query_id") or row["query"]
        out[key] = float(row["semantic_top1"][1])
    return out


def _fmt_delta(new: float, old: float) -> str:
    delta = new - old
    return f"{delta:+.4f}"


def compare_summaries(old: dict, new: dict) -> str:
    old_suites = suites(old)
    new_suites = suites(new)
    names = sorted(set(old_suites) & set(new_suites))
    lines: list[str] = ["# Eval comparison\n"]
    if not names:
        lines.append("No overlapping suites.\n")
        return "\n".join(lines)

    lines.append("## Aggregate deltas\n")
    header = ["Suite", "Method"] + metrics.METRIC_NAMES
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|---|---|" + "|".join(["---:"] * len(metrics.METRIC_NAMES)) + "|")
    for name in names:
        for method in ("semantic", "keyword"):
            old_agg = old_suites[name]["aggregate"][method]
            new_agg = new_suites[name]["aggregate"][method]
            deltas = [_fmt_delta(new_agg[m], old_agg[m]) for m in metrics.METRIC_NAMES]
            lines.append(f"| {name} | {method} | " + " | ".join(deltas) + " |")

    lines.append("\n## Rank movements\n")
    lines.append("| Suite | Query | Old | New | Delta |")
    lines.append("|---|---|---:|---:|---:|")
    for name in names:
        old_ranks = _rank_map(old_suites[name])
        new_ranks = _rank_map(new_suites[name])
        for key in sorted(set(old_ranks) & set(new_ranks)):
            old_rank = old_ranks[key]
            new_rank = new_ranks[key]
            if old_rank == new_rank:
                continue
            old_val = old_rank if old_rank is not None else 9999
            new_val = new_rank if new_rank is not None else 9999
            delta = new_val - old_val
            lines.append(f"| {name} | {str(key)[:70]} | {old_rank or 'NF'} | {new_rank or 'NF'} | {delta:+d} |")

    lines.append("\n## Null top-score deltas\n")
    lines.append("| Suite | Query | Old | New | Delta |")
    lines.append("|---|---|---:|---:|---:|")
    for name in names:
        old_nulls = _null_scores(old_suites[name])
        new_nulls = _null_scores(new_suites[name])
        for key in sorted(set(old_nulls) & set(new_nulls)):
            old_score = old_nulls[key]
            new_score = new_nulls[key]
            if abs(new_score - old_score) < 0.0001:
                continue
            lines.append(
                f"| {name} | {str(key)[:70]} | {old_score:.4f} | {new_score:.4f} | {_fmt_delta(new_score, old_score)} |"
            )

    lines.append("\n## Timing deltas\n")
    lines.append("| Suite | Metric | Old mean | New mean | Delta |")
    lines.append("|---|---|---:|---:|---:|")
    for name in names:
        old_timing = old_suites[name].get("timing", {})
        new_timing = new_suites[name].get("timing", {})
        for metric_name in sorted(set(old_timing) & set(new_timing)):
            old_mean = float(old_timing[metric_name].get("mean", 0.0))
            new_mean = float(new_timing[metric_name].get("mean", 0.0))
            lines.append(
                f"| {name} | {metric_name} | {old_mean:.4f} | {new_mean:.4f} | {_fmt_delta(new_mean, old_mean)} |"
            )
    return "\n".join(lines) + "\n"


def next_version(prefix: str, suffix: str, directory: Path) -> int:
    n = 1
    while (directory / f"{prefix}_v{n}{suffix}").exists():
        n += 1
    return n


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = compare_summaries(load_summary(args.old), load_summary(args.new))
    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        out_dir = Path(__file__).resolve().parent
        version = next_version("comparison", ".md", out_dir)
        out = out_dir / f"comparison_v{version}.md"
        out.write_text(report, encoding="utf-8")
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
