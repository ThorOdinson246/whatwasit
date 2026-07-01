"""Standard information-retrieval metrics for the hist search evaluation.

All metrics assume at most one relevant document per query (our ground truth is
a single ``correct_session_id``), which simplifies the definitions:

- Precision@k = (1 if the correct id is in the top k else 0) / k
- Recall@k    = 1 if the correct id is in the top k else 0   (one relevant doc)
- RR          = 1 / rank of the correct id (0 if not retrieved)
- nDCG@k      = 1 / log2(rank + 1) if rank <= k else 0        (IDCG = 1)

A ranked result is a list of session-id strings, best first.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional


def rank_of(ranked: List[str], gold: str) -> Optional[int]:
    """1-based rank of ``gold`` in ``ranked``, or ``None`` if absent."""
    for i, sid in enumerate(ranked):
        if sid == gold:
            return i + 1
    return None


def precision_at_k(ranked: List[str], gold: str, k: int) -> float:
    r = rank_of(ranked[:k], gold)
    return (1.0 / k) if r is not None else 0.0


def recall_at_k(ranked: List[str], gold: str, k: int) -> float:
    return 1.0 if rank_of(ranked[:k], gold) is not None else 0.0


def reciprocal_rank(ranked: List[str], gold: str) -> float:
    r = rank_of(ranked, gold)
    return (1.0 / r) if r is not None else 0.0


def ndcg_at_k(ranked: List[str], gold: str, k: int) -> float:
    r = rank_of(ranked[:k], gold)
    if r is None:
        return 0.0
    return 1.0 / math.log2(r + 1)  # IDCG = 1/log2(2) = 1 for a single relevant doc


METRIC_KS = {
    "P@1": ("precision", 1),
    "P@3": ("precision", 3),
    "P@5": ("precision", 5),
    "R@5": ("recall", 5),
    "R@10": ("recall", 10),
    "nDCG@5": ("ndcg", 5),
}


def per_query_metrics(ranked: List[str], gold: str) -> Dict[str, float]:
    """Compute the full metric set for one (ranked, gold) pair."""
    out: Dict[str, float] = {}
    for name, (kind, k) in METRIC_KS.items():
        if kind == "precision":
            out[name] = precision_at_k(ranked, gold, k)
        elif kind == "recall":
            out[name] = recall_at_k(ranked, gold, k)
        elif kind == "ndcg":
            out[name] = ndcg_at_k(ranked, gold, k)
    out["MRR"] = reciprocal_rank(ranked, gold)
    return out


METRIC_NAMES = ["P@1", "P@3", "P@5", "R@5", "R@10", "MRR", "nDCG@5"]


def aggregate(rows: List[Dict[str, float]]) -> Dict[str, float]:
    """Mean each metric over a list of per-query metric dicts."""
    if not rows:
        return {name: 0.0 for name in METRIC_NAMES}
    return {
        name: sum(r[name] for r in rows) / len(rows) for name in METRIC_NAMES
    }
