"""Run whatwasit search-quality eval suites.

Default invocation preserves the historical behavior: run the standard suite
and the keyword-heavy breakout, write versioned artifacts, and keep the
standard suite at the top level of ``summary_vN.json`` for compatibility.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from whatwasit import db
from whatwasit.config import Config
from whatwasit.embedder import build_embedder, encode_passages, encode_query_one
from whatwasit.index import build_index
from whatwasit.models import Command, Session
from whatwasit.search import search

from eval import baseline, metrics
from eval.dataset_io import dataset_stats, load_jsonl, validate_queries, validate_sessions
from eval.suites import EvalSuite, available_suites, get_suite

EVAL_DIR = Path(__file__).resolve().parent


def next_version(prefix: str, suffix: str) -> int:
    n = 1
    while (EVAL_DIR / f"{prefix}_v{n}{suffix}").exists():
        n += 1
    return n


def stat(xs: Sequence[float]) -> dict:
    if not xs:
        return {"mean": 0.0, "p50": 0.0, "p95": 0.0, "min": 0.0, "max": 0.0}
    xs2 = sorted(xs)
    return {
        "mean": round(statistics.mean(xs), 4),
        "p50": round(statistics.median(xs), 4),
        "p95": round(xs2[min(len(xs2) - 1, int(0.95 * len(xs2)))], 4),
        "min": round(xs2[0], 4),
        "max": round(xs2[-1], 4),
    }


def resolve_retrieval_limit(mode: str, config: Config, n_sessions: int) -> tuple[int, str]:
    if mode == "full":
        return n_sessions, "full"
    if mode == "production":
        return config.top_k, "production"
    try:
        k = int(mode)
    except ValueError as exc:
        raise SystemExit("--retrieval-k must be full, production, or a positive integer") from exc
    if k <= 0:
        raise SystemExit("--retrieval-k integer must be positive")
    return k, str(k)


def index_sessions(config: Config, sessions: List[dict], embedder, index):
    """Index eval sessions through the real store. Returns id maps + corpus."""
    conn = db.connect(config.db_path)
    db.initialize(conn)
    db.reset(conn)

    str_to_db: Dict[str, int] = {}
    db_to_str: Dict[int, str] = {}
    corpus: Dict[str, str] = {}
    doc_texts: List[str] = []
    db_ids: List[int] = []

    base_ts = 1_700_000_000
    for si, s in enumerate(sessions):
        cmds = [
            Command(raw_cmd=c, ts=base_ts + si * 10_000 + ci * 30, source="eval", cwd=s["cwd"])
            for ci, c in enumerate(s["commands"])
        ]
        session = Session(
            commands=cmds,
            start_ts=cmds[0].ts,
            end_ts=cmds[-1].ts,
            cwd=s["cwd"],
        )
        session.doc_text = session.to_document()
        db_id = db.insert_session(conn, session)
        str_to_db[s["session_id"]] = db_id
        db_to_str[db_id] = s["session_id"]
        corpus[s["session_id"]] = session.doc_text
        doc_texts.append(session.doc_text)
        db_ids.append(db_id)

    conn.commit()
    conn.close()

    vectors = encode_passages(embedder, doc_texts)
    index.add(db_ids, vectors)
    index.save()
    return str_to_db, db_to_str, corpus


def evaluate_suite(
    suite: EvalSuite,
    *,
    retrieval_k: str,
    model_name: str,
    embedding_dim: int,
    ranking_variant: str,
) -> tuple[dict, list[dict]]:
    sessions = load_jsonl(suite.sessions_path)
    queries = load_jsonl(suite.queries_path)
    validate_sessions(sessions)
    validate_queries(queries, {row["session_id"] for row in sessions})

    tmp = tempfile.mkdtemp(prefix=f"hist_eval_{suite.name}_")
    config = Config(data_dir=Path(tmp), model_name=model_name, embedding_dim=embedding_dim)
    config.ensure_data_dir()
    embedder = build_embedder(config)
    index = build_index(config)

    n_sessions = len(sessions)
    limit, retrieval_label = resolve_retrieval_limit(retrieval_k, config, n_sessions)

    print(
        f"[{suite.name}] Indexing {n_sessions} sessions through the real whatwasit pipeline ...",
        flush=True,
    )
    embedder.encode(["warmup"])
    _str_to_db, db_to_str, corpus = index_sessions(config, sessions, embedder, index)

    answerable = [q for q in queries if q["correct_session_id"] is not None]
    nulls = [q for q in queries if q["correct_session_id"] is None]
    print(
        f"[{suite.name}] Running {len(queries)} queries "
        f"({len(answerable)} answerable + {len(nulls)} null) x 2 methods ...",
        flush=True,
    )

    raw_records: List[dict] = []
    per_query: List[dict] = []
    sem_rows_by_topic: Dict[str, List[dict]] = {}
    kw_rows_by_topic: Dict[str, List[dict]] = {}
    sem_rows_all: List[dict] = []
    kw_rows_all: List[dict] = []

    embed_ms_list: List[float] = []
    ann_ms_list: List[float] = []
    total_ms_list: List[float] = []
    answerable_top1_sem: List[float] = []
    answerable_top1_kw: List[float] = []

    for q in queries:
        query = q["query"]
        gold = q["correct_session_id"]
        topic = q["topic"]

        t0 = time.perf_counter()
        qv = encode_query_one(embedder, query)
        t_embed = (time.perf_counter() - t0) * 1000.0
        t0 = time.perf_counter()
        _ = index.search(qv, limit)
        t_ann = (time.perf_counter() - t0) * 1000.0

        t0 = time.perf_counter()
        results = search(config, query, k=limit, embedder=embedder, index=index)
        t_total = (time.perf_counter() - t0) * 1000.0

        sem_ranked_ids = [db_to_str.get(r.session.id, f"?{r.session.id}") for r in results]
        sem_scores = {
            db_to_str.get(r.session.id, f"?{r.session.id}"): float(r.score)
            for r in results
        }

        t0 = time.perf_counter()
        kw_scored = baseline.rank(query, corpus)
        t_kw = (time.perf_counter() - t0) * 1000.0
        kw_ranked_ids = [sid for sid, _ in kw_scored]
        kw_scores = {sid: float(sc) for sid, sc in kw_scored}

        embed_ms_list.append(t_embed)
        ann_ms_list.append(t_ann)
        total_ms_list.append(t_total)

        sem_full = [
            {"rank": i + 1, "session_id": sid, "score": round(sem_scores.get(sid, 0.0), 6)}
            for i, sid in enumerate(sem_ranked_ids)
        ]
        kw_full = [
            {"rank": i + 1, "session_id": sid, "score": round(sc, 6)}
            for i, (sid, sc) in enumerate(kw_scored)
        ]

        raw_records.append(
            {
                "suite": suite.name,
                "query": query,
                "topic": topic,
                "correct_session_id": gold,
                "method": "semantic",
                "timing_ms": {
                    "embed": round(t_embed, 3),
                    "ann": round(t_ann, 3),
                    "total": round(t_total, 3),
                },
                "ranked": sem_full,
            }
        )
        raw_records.append(
            {
                "suite": suite.name,
                "query": query,
                "topic": topic,
                "correct_session_id": gold,
                "method": "keyword",
                "timing_ms": {"total": round(t_kw, 3)},
                "ranked": kw_full,
            }
        )

        if gold is not None:
            sem_m = metrics.per_query_metrics(sem_ranked_ids, gold)
            kw_m = metrics.per_query_metrics(kw_ranked_ids, gold)
            sem_rank = metrics.rank_of(sem_ranked_ids, gold)
            kw_rank = metrics.rank_of(kw_ranked_ids, gold)
            sem_rows_all.append(sem_m)
            kw_rows_all.append(kw_m)
            sem_rows_by_topic.setdefault(topic, []).append(sem_m)
            kw_rows_by_topic.setdefault(topic, []).append(kw_m)
            if sem_rank == 1 and sem_ranked_ids:
                answerable_top1_sem.append(sem_scores.get(sem_ranked_ids[0], 0.0))
            if kw_rank == 1 and kw_ranked_ids:
                answerable_top1_kw.append(kw_scores.get(kw_ranked_ids[0], 0.0))
            per_query.append(
                {
                    "query": query,
                    "query_id": q.get("query_id"),
                    "kind": q.get("kind"),
                    "topic": topic,
                    "gold": gold,
                    "semantic": {
                        "rank": sem_rank,
                        "top3": [
                            (sid, round(sem_scores.get(sid, 0.0), 4))
                            for sid in sem_ranked_ids[:3]
                        ],
                        "metrics": sem_m,
                    },
                    "keyword": {
                        "rank": kw_rank,
                        "top3": [
                            (sid, round(kw_scores.get(sid, 0.0), 4))
                            for sid in kw_ranked_ids[:3]
                        ],
                        "metrics": kw_m,
                    },
                }
            )
        else:
            sem_top1 = (
                (sem_ranked_ids[0], round(sem_scores.get(sem_ranked_ids[0], 0.0), 4))
                if sem_ranked_ids
                else (None, 0.0)
            )
            kw_top1 = (
                (kw_ranked_ids[0], round(kw_scores.get(kw_ranked_ids[0], 0.0), 4))
                if kw_ranked_ids
                else (None, 0.0)
            )
            per_query.append(
                {
                    "query": query,
                    "query_id": q.get("query_id"),
                    "kind": q.get("kind"),
                    "topic": topic,
                    "gold": None,
                    "semantic": {
                        "rank": None,
                        "top1": sem_top1,
                        "top3": [
                            (sid, round(sem_scores.get(sid, 0.0), 4))
                            for sid in sem_ranked_ids[:3]
                        ],
                    },
                    "keyword": {
                        "rank": None,
                        "top1": kw_top1,
                        "top3": [
                            (sid, round(kw_scores.get(sid, 0.0), 4))
                            for sid in kw_ranked_ids[:3]
                        ],
                    },
                }
            )

    agg = {"semantic": metrics.aggregate(sem_rows_all), "keyword": metrics.aggregate(kw_rows_all)}
    per_topic = {
        topic: {
            "n": len(sem_rows_by_topic[topic]),
            "semantic": metrics.aggregate(sem_rows_by_topic[topic]),
            "keyword": metrics.aggregate(kw_rows_by_topic[topic]),
        }
        for topic in sorted(sem_rows_by_topic)
    }

    null_details = []
    sem_null_top1 = []
    kw_null_top1 = []
    for q in nulls:
        pq = next(p for p in per_query if p["query"] == q["query"])
        sem_top1_score = pq["semantic"]["top1"][1]
        kw_top1_score = pq["keyword"]["top1"][1]
        sem_null_top1.append(sem_top1_score)
        kw_null_top1.append(kw_top1_score)
        null_details.append(
            {
                "query": q["query"],
                "query_id": q.get("query_id"),
                "topic": q["topic"],
                "semantic_top1": pq["semantic"]["top1"],
                "keyword_top1": pq["keyword"]["top1"],
            }
        )

    sweep = []
    for t in [0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]:
        sem_fp = sum(1 for s in sem_null_top1 if s >= t) / len(sem_null_top1) if sem_null_top1 else 0.0
        sem_suppress = (
            sum(1 for s in answerable_top1_sem if s < t) / len(answerable_top1_sem)
            if answerable_top1_sem
            else 0.0
        )
        sweep.append(
            {
                "threshold": t,
                "semantic_null_fp_rate": round(sem_fp, 4),
                "semantic_answerable_suppressed": round(sem_suppress, 4),
            }
        )

    stats = dataset_stats(sessions, queries)
    n_labeled = sum(1 for s in sessions if s.get("topic") != "distractor")
    n_distract = sum(1 for s in sessions if s.get("topic") == "distractor")

    suite_summary = {
        "suite": suite.name,
        "label": suite.label,
        "n_sessions": stats.sessions,
        "n_labeled": n_labeled,
        "n_distractor": n_distract,
        "n_queries": stats.queries,
        "n_answerable": stats.answerable,
        "n_null": stats.null,
        "model": config.model_name,
        "embedding_dim": config.embedding_dim,
        "run": {
            "retrieval_k": retrieval_label,
            "retrieval_limit": limit,
            "production_top_k": config.top_k,
            "ranking_variant": ranking_variant,
        },
        "search_config": {
            "hybrid_search": config.hybrid_search,
            "hybrid_literal_only": True,
        },
        "aggregate": agg,
        "per_topic": per_topic,
        "null_analysis": {
            "details": null_details,
            "threshold_sweep": sweep,
            "answerable_top1_semantic": stat(answerable_top1_sem),
            "null_top1_semantic": stat(sem_null_top1),
            "answerable_top1_keyword_raw": answerable_top1_kw,
            "null_top1_keyword_raw": kw_null_top1,
        },
        "timing": {
            "semantic_embed_ms": stat(embed_ms_list),
            "semantic_ann_ms": stat(ann_ms_list),
            "semantic_total_ms": stat(total_ms_list),
        },
        "per_query": per_query,
    }
    return suite_summary, raw_records


def render_suite_tables(name: str, summary: dict) -> list[str]:
    M = metrics.METRIC_NAMES
    lines: list[str] = []
    lines.append(f"\n## Suite: {name}\n")
    lines.append(
        f"Corpus: {summary['n_sessions']} sessions "
        f"({summary['n_labeled']} labeled + {summary['n_distractor']} distractor). "
        f"Queries: {summary['n_answerable']} answerable + {summary['n_null']} null. "
        f"Retrieval: `{summary['run']['retrieval_k']}`. "
        f"Model: `{summary['model']}` ({summary['embedding_dim']}-dim).\n"
    )
    lines.append("\n### Aggregate: semantic vs keyword\n")
    lines.append("| Method | " + " | ".join(M) + " |")
    lines.append("|---|" + "|".join(["---:"] * len(M)) + "|")
    for method in ("semantic", "keyword"):
        lines.append("| " + method + " | " + " | ".join(f"{summary['aggregate'][method][m]:.3f}" for m in M) + " |")

    lines.append("\n### Per-topic (semantic / keyword)\n")
    lines.append("| Topic | n | " + " | ".join(M) + " |")
    lines.append("|---|--:|" + "|".join(["---:"] * len(M)) + "|")
    for topic in sorted(summary["per_topic"]):
        pt = summary["per_topic"][topic]
        sem = " | ".join(f"{pt['semantic'][m]:.2f}" for m in M)
        lines.append(f"| {topic} (sem) | {pt['n']} | " + sem + " |")
        kw = " | ".join(f"{pt['keyword'][m]:.2f}" for m in M)
        lines.append(f"| {topic} (kw) | {pt['n']} | " + kw + " |")

    lines.append("\n### Per-query (answerable): semantic rank & top-3 vs keyword rank\n")
    lines.append("| Query | Expected | Sem rank | Sem top-3 (id:score) | KW rank |")
    lines.append("|---|---|--:|---|--:|")
    for p in summary["per_query"]:
        if p["gold"] is None:
            continue
        q = p["query"] if len(p["query"]) <= 70 else p["query"][:67] + "..."
        sem_rank = p["semantic"]["rank"] if p["semantic"]["rank"] is not None else "NF"
        kw_rank = p["keyword"]["rank"] if p["keyword"]["rank"] is not None else "NF"
        top3 = "<br>".join(f"{sid}:{sc}" for sid, sc in p["semantic"]["top3"])
        lines.append(f"| {q} | {p['gold']} | {sem_rank} | {top3} | {kw_rank} |")

    if summary["n_null"]:
        lines.append("\n### Null queries (no correct session): top-1 returned\n")
        lines.append("| Query | Sem top-1 (id:score) | KW top-1 (id:score) |")
        lines.append("|---|---|---|")
        for p in summary["per_query"]:
            if p["gold"] is not None:
                continue
            q = p["query"] if len(p["query"]) <= 70 else p["query"][:67] + "..."
            st = p["semantic"]["top1"]
            kt = p["keyword"]["top1"]
            lines.append(f"| {q} | {st[0]}:{st[1]} | {kt[0]}:{kt[1]} |")
    return lines


def render_tables(summary: dict) -> str:
    lines: List[str] = ["# Eval tables (auto-generated)\n"]
    for name, suite_summary in summary["suites"].items():
        lines.extend(render_suite_tables(name, suite_summary))
    return "\n".join(lines) + "\n"


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--suite", choices=sorted(available_suites()))
    group.add_argument("--all-suites", action="store_true")
    parser.add_argument("--retrieval-k", default="full", help="full, production, or a positive integer")
    parser.add_argument("--model-name", default=Config().model_name)
    parser.add_argument("--embedding-dim", type=int, default=Config().embedding_dim)
    parser.add_argument("--ranking-variant", default="production")
    return parser.parse_args(argv)


def selected_suites(args: argparse.Namespace) -> list[EvalSuite]:
    if args.all_suites:
        return list(available_suites().values())
    if args.suite:
        return [get_suite(args.suite)]
    # Historical default: standard plus keyword-heavy breakout when present.
    names = ["standard", "keyword_heavy"]
    return [get_suite(name) for name in names if get_suite(name).exists()]


def run(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    suites = selected_suites(args)
    if not suites:
        raise SystemExit("no eval suites selected")

    all_raw: list[dict] = []
    suite_summaries: dict[str, dict] = {}
    for suite in suites:
        suite_summary, raw = evaluate_suite(
            suite,
            retrieval_k=args.retrieval_k,
            model_name=args.model_name,
            embedding_dim=args.embedding_dim,
            ranking_variant=args.ranking_variant,
        )
        suite_summaries[suite.name] = suite_summary
        all_raw.extend(raw)

    standard = suite_summaries.get("standard") or next(iter(suite_summaries.values()))
    summary = {
        "run": {
            "retrieval_k": standard["run"]["retrieval_k"],
            "retrieval_limit": standard["run"]["retrieval_limit"],
            "production_top_k": standard["run"]["production_top_k"],
            "ranking_variant": standard["run"]["ranking_variant"],
            "suites": list(suite_summaries),
        },
        "suites": suite_summaries,
        # Backward-compatible standard-suite fields.
        **{k: v for k, v in standard.items() if k not in {"suite", "label"}},
    }
    if "keyword_heavy" in suite_summaries:
        kh = suite_summaries["keyword_heavy"]
        summary["keyword_heavy"] = {
            "n_queries": kh["n_queries"],
            "aggregate": kh["aggregate"],
            "per_query": kh["per_query"],
        }

    v = next_version("results_raw", ".jsonl")
    raw_path = EVAL_DIR / f"results_raw_v{v}.jsonl"
    with raw_path.open("w", encoding="utf-8") as f:
        for rec in all_raw:
            f.write(json.dumps(rec) + "\n")

    csv_path = EVAL_DIR / f"metrics_summary_v{v}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["suite", "method", "scope", "n_queries", "retrieval_k"] + metrics.METRIC_NAMES)
        for suite_name, suite_summary in suite_summaries.items():
            for method in ("semantic", "keyword"):
                w.writerow(
                    [
                        suite_name,
                        method,
                        "overall",
                        suite_summary["n_answerable"],
                        suite_summary["run"]["retrieval_k"],
                    ]
                    + [round(suite_summary["aggregate"][method][m], 4) for m in metrics.METRIC_NAMES]
                )
            for topic in sorted(suite_summary["per_topic"]):
                for method in ("semantic", "keyword"):
                    w.writerow(
                        [
                            suite_name,
                            method,
                            f"topic:{topic}",
                            suite_summary["per_topic"][topic]["n"],
                            suite_summary["run"]["retrieval_k"],
                        ]
                        + [
                            round(suite_summary["per_topic"][topic][method][m], 4)
                            for m in metrics.METRIC_NAMES
                        ]
                    )

    json_path = EVAL_DIR / f"summary_v{v}.json"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    tables_path = EVAL_DIR / f"tables_v{v}.md"
    tables_path.write_text(render_tables(summary), encoding="utf-8")

    for suite_name, suite_summary in suite_summaries.items():
        print(f"\n=== {suite_name.upper()} (over {suite_summary['n_answerable']} answerable queries) ===", flush=True)
        hdr = "method    " + "  ".join(f"{m:>7}" for m in metrics.METRIC_NAMES)
        print(hdr)
        for method in ("semantic", "keyword"):
            print(
                f"{method:<9} "
                + "  ".join(f"{suite_summary['aggregate'][method][m]:7.3f}" for m in metrics.METRIC_NAMES)
            )
    print(f"\nwrote {raw_path.name}, {csv_path.name}, {json_path.name}, {tables_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
