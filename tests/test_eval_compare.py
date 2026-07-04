from __future__ import annotations

from eval.compare import compare_summaries


def _suite(p1: float, rank: int | None, null_score: float) -> dict:
    metric_names = ["P@1", "P@3", "P@5", "R@5", "R@10", "MRR", "nDCG@5"]
    agg = {name: 0.0 for name in metric_names}
    agg["P@1"] = p1
    return {
        "aggregate": {"semantic": agg, "keyword": dict(agg)},
        "per_query": [
            {
                "query_id": "q1",
                "query": "query",
                "gold": "s1",
                "semantic": {"rank": rank},
            }
        ],
        "null_analysis": {
            "details": [
                {"query_id": "n1", "query": "null", "semantic_top1": ["s2", null_score]}
            ]
        },
        "timing": {"semantic_total_ms": {"mean": 10.0}},
    }


def test_compare_summaries_reports_metric_and_rank_deltas() -> None:
    old = {"suites": {"standard": _suite(0.5, 3, 0.2)}}
    new = {"suites": {"standard": _suite(0.75, 1, 0.3)}}
    new["suites"]["standard"]["timing"]["semantic_total_ms"]["mean"] = 12.5

    report = compare_summaries(old, new)

    assert "| standard | semantic | +0.2500" in report
    assert "| standard | q1 | 3 | 1 | -2 |" in report
    assert "| standard | n1 | 0.2000 | 0.3000 | +0.1000 |" in report
    assert "| standard | semantic_total_ms | 10.0000 | 12.5000 | +2.5000 |" in report


def test_compare_summaries_accepts_legacy_flat_summary() -> None:
    report = compare_summaries(_suite(0.5, 2, 0.1), _suite(0.5, 1, 0.1))
    assert "| standard | q1 | 2 | 1 | -1 |" in report
