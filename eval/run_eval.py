"""Run the hist search-quality evaluation: semantic vs keyword baseline.

Pipeline:
  1. Load eval/sessions.jsonl and eval/queries.jsonl.
  2. Index every session through hist's real components (SQLite + embedder +
     usearch), keeping a stable string-id <-> db-id map.
  3. For each query, retrieve with:
       - semantic: hist.search.search() (the actual production search path)
       - keyword : eval.baseline.rank() over the same session documents
  4. Compute IR metrics (P@1/3/5, R@5/10, MRR, nDCG@5) per query and aggregate
     overall and per-topic.
  5. Capture per-query timings (query-embed, ANN search, full search) and the
     full ranked list *with raw scores* for every query and both methods.
  6. Write versioned, durable artifacts (never overwritten between runs):
       eval/results_raw_v{N}.jsonl   -- full ranked lists + scores + timings
       eval/metrics_summary_v{N}.csv -- aggregate + per-topic, both methods
       eval/summary_v{N}.json        -- everything, for report/plot building
       eval/tables_v{N}.md           -- ready-to-read aggregate + per-query tables

Fully offline; uses the local cached MiniLM model.
"""

from __future__ import annotations

import csv
import json
import os
import statistics
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hist import db
from hist.config import Config
from hist.embedder import build_embedder, encode_passages, encode_query_one
from hist.index import build_index
from hist.models import Command, Session
from hist.search import search

from eval import baseline, metrics

EVAL_DIR = Path(__file__).resolve().parent


def load_jsonl(path: Path) -> List[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def next_version(prefix: str, suffix: str) -> int:
    n = 1
    while (EVAL_DIR / f"{prefix}_v{n}{suffix}").exists():
        n += 1
    return n


def index_sessions(config: Config, sessions: List[dict], embedder, index):
    """Index eval sessions through the real store. Returns id maps + corpus."""
    conn = db.connect(config.db_path)
    db.initialize(conn)
    db.reset(conn)

    str_to_db: Dict[str, int] = {}
    db_to_str: Dict[int, str] = {}
    corpus: Dict[str, str] = {}  # string id -> doc text (for baseline)
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


def run() -> int:
    sessions = load_jsonl(EVAL_DIR / "sessions.jsonl")
    queries = load_jsonl(EVAL_DIR / "queries.jsonl")
    n_sessions = len(sessions)

    tmp = tempfile.mkdtemp(prefix="hist_eval_")
    config = Config(data_dir=Path(tmp))
    config.ensure_data_dir()
    embedder = build_embedder(config)
    index = build_index(config)

    print(f"Indexing {n_sessions} sessions through the real hist pipeline ...", flush=True)
    embedder.encode(["warmup"])  # load model, excluded from timings
    str_to_db, db_to_str, corpus = index_sessions(config, sessions, embedder, index)

    answerable = [q for q in queries if q["correct_session_id"] is not None]
    nulls = [q for q in queries if q["correct_session_id"] is None]
    print(f"Running {len(queries)} queries ({len(answerable)} answerable + {len(nulls)} null) "
          f"x 2 methods ...", flush=True)

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

        # --- semantic: component timings (query embed + ANN) ---
        t0 = time.perf_counter()
        qv = encode_query_one(embedder, query)
        t_embed = (time.perf_counter() - t0) * 1000.0
        t0 = time.perf_counter()
        _ = index.search(qv, n_sessions)
        t_ann = (time.perf_counter() - t0) * 1000.0

        # --- semantic: official ranking through hist's actual search() ---
        t0 = time.perf_counter()
        results = search(config, query, k=n_sessions, embedder=embedder, index=index)
        t_total = (time.perf_counter() - t0) * 1000.0

        sem_ranked_ids = [db_to_str.get(r.session.id, f"?{r.session.id}") for r in results]
        sem_scores = {db_to_str.get(r.session.id, f"?{r.session.id}"): float(r.score) for r in results}

        # --- keyword baseline over the same documents ---
        t0 = time.perf_counter()
        kw_scored = baseline.rank(query, corpus)
        t_kw = (time.perf_counter() - t0) * 1000.0
        kw_ranked_ids = [sid for sid, _ in kw_scored]
        kw_scores = {sid: float(sc) for sid, sc in kw_scored}

        embed_ms_list.append(t_embed)
        ann_ms_list.append(t_ann)
        total_ms_list.append(t_total)

        # full ranked lists with scores for the raw log
        sem_full = [
            {"rank": i + 1, "session_id": sid, "score": round(sem_scores.get(sid, 0.0), 6)}
            for i, sid in enumerate(sem_ranked_ids)
        ]
        kw_full = [
            {"rank": i + 1, "session_id": sid, "score": round(sc, 6)}
            for i, (sid, sc) in enumerate(kw_scored)
        ]

        raw_records.append({
            "query": query, "topic": topic, "correct_session_id": gold,
            "method": "semantic",
            "timing_ms": {"embed": round(t_embed, 3), "ann": round(t_ann, 3), "total": round(t_total, 3)},
            "ranked": sem_full,
        })
        raw_records.append({
            "query": query, "topic": topic, "correct_session_id": gold,
            "method": "keyword",
            "timing_ms": {"total": round(t_kw, 3)},
            "ranked": kw_full,
        })

        if gold is not None:
            sem_m = metrics.per_query_metrics(sem_ranked_ids, gold)
            kw_m = metrics.per_query_metrics(kw_ranked_ids, gold)
            sem_rank = metrics.rank_of(sem_ranked_ids, gold)
            kw_rank = metrics.rank_of(kw_ranked_ids, gold)
            sem_rows_all.append(sem_m)
            kw_rows_all.append(kw_m)
            sem_rows_by_topic.setdefault(topic, []).append(sem_m)
            kw_rows_by_topic.setdefault(topic, []).append(kw_m)
            if sem_rank == 1:
                answerable_top1_sem.append(sem_scores.get(sem_ranked_ids[0], 0.0))
            if kw_rank == 1:
                answerable_top1_kw.append(kw_scores.get(kw_ranked_ids[0], 0.0))
            per_query.append({
                "query": query, "topic": topic, "gold": gold,
                "semantic": {"rank": sem_rank,
                              "top3": [(sid, round(sem_scores.get(sid, 0.0), 4)) for sid in sem_ranked_ids[:3]],
                              "metrics": sem_m},
                "keyword": {"rank": kw_rank,
                             "top3": [(sid, round(kw_scores.get(sid, 0.0), 4)) for sid in kw_ranked_ids[:3]],
                             "metrics": kw_m},
            })
        else:
            per_query.append({
                "query": query, "topic": topic, "gold": None,
                "semantic": {"rank": None,
                              "top1": (sem_ranked_ids[0], round(sem_scores.get(sem_ranked_ids[0], 0.0), 4)),
                              "top3": [(sid, round(sem_scores.get(sid, 0.0), 4)) for sid in sem_ranked_ids[:3]]},
                "keyword": {"rank": None,
                             "top1": (kw_ranked_ids[0], round(kw_scores.get(kw_ranked_ids[0], 0.0), 4)),
                             "top3": [(sid, round(kw_scores.get(sid, 0.0), 4)) for sid in kw_ranked_ids[:3]]},
            })

    agg = {"semantic": metrics.aggregate(sem_rows_all), "keyword": metrics.aggregate(kw_rows_all)}
    per_topic = {}
    for topic in sorted(sem_rows_by_topic):
        per_topic[topic] = {
            "n": len(sem_rows_by_topic[topic]),
            "semantic": metrics.aggregate(sem_rows_by_topic[topic]),
            "keyword": metrics.aggregate(kw_rows_by_topic[topic]),
        }

    # --- null-query false-positive analysis (score threshold sweep) ---
    null_details = []
    sem_null_top1 = []
    kw_null_top1 = []
    for q in nulls:
        pq = next(p for p in per_query if p["query"] == q["query"])
        sem_top1_score = pq["semantic"]["top1"][1]
        kw_top1_score = pq["keyword"]["top1"][1]
        sem_null_top1.append(sem_top1_score)
        kw_null_top1.append(kw_top1_score)
        null_details.append({
            "query": q["query"], "topic": q["topic"],
            "semantic_top1": pq["semantic"]["top1"],
            "keyword_top1": pq["keyword"]["top1"],
        })

    sweep = []
    for t in [0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]:
        sem_fp = sum(1 for s in sem_null_top1 if s >= t) / len(sem_null_top1) if sem_null_top1 else 0.0
        # fraction of answerable-correct@1 queries that WOULD be suppressed at t
        sem_suppress = (sum(1 for s in answerable_top1_sem if s < t) / len(answerable_top1_sem)
                        if answerable_top1_sem else 0.0)
        sweep.append({"threshold": t,
                      "semantic_null_fp_rate": round(sem_fp, 4),
                      "semantic_answerable_suppressed": round(sem_suppress, 4)})

    def stat(xs):
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

    timing = {
        "semantic_embed_ms": stat(embed_ms_list),
        "semantic_ann_ms": stat(ann_ms_list),
        "semantic_total_ms": stat(total_ms_list),
    }

    n_labeled = sum(1 for s in sessions if s.get("topic") != "distractor")
    n_distract = sum(1 for s in sessions if s.get("topic") == "distractor")

    summary = {
        "n_sessions": n_sessions, "n_labeled": n_labeled, "n_distractor": n_distract,
        "n_queries": len(queries), "n_answerable": len(answerable), "n_null": len(nulls),
        "model": config.model_name, "embedding_dim": config.embedding_dim,
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
        "timing": timing,
        "per_query": per_query,
    }

    # --- optional keyword-heavy breakout ----------------------------
    kh_path = EVAL_DIR / "queries_keyword_heavy.jsonl"
    if kh_path.exists():
        kh_queries = load_jsonl(kh_path)
        print(f"Running {len(kh_queries)} keyword-heavy queries ...", flush=True)
        kh_rows_sem: List[dict] = []
        kh_rows_kw:  List[dict] = []
        kh_per_query: List[dict] = []
        for kq in kh_queries:
            query  = kq["query"]
            gold   = kq["correct_session_id"]
            topic  = kq["topic"]
            kh_results_ = search(config, query, k=n_sessions, embedder=embedder, index=index)
            kh_sem_ids   = [db_to_str.get(r.session.id, f"?{r.session.id}") for r in kh_results_]
            kh_sem_sc    = {db_to_str.get(r.session.id, f"?{r.session.id}"): float(r.score) for r in kh_results_}
            kh_kw_scored = baseline.rank(query, corpus)
            kh_kw_ids    = [sid for sid, _ in kh_kw_scored]
            kh_kw_sc     = {sid: float(sc) for sid, sc in kh_kw_scored}
            sem_m = metrics.per_query_metrics(kh_sem_ids, gold)
            kw_m  = metrics.per_query_metrics(kh_kw_ids, gold)
            kh_rows_sem.append(sem_m); kh_rows_kw.append(kw_m)
            kh_per_query.append({
                "query": query, "topic": topic, "gold": gold,
                "semantic": {"rank": metrics.rank_of(kh_sem_ids, gold),
                             "top3": [(sid, round(kh_sem_sc.get(sid, 0.0), 4))
                                      for sid in kh_sem_ids[:3]],
                             "metrics": sem_m},
                "keyword":  {"rank": metrics.rank_of(kh_kw_ids, gold),
                             "top3": [(sid, round(kh_kw_sc.get(sid, 0.0), 4))
                                      for sid in kh_kw_ids[:3]],
                             "metrics": kw_m},
            })
        kh_agg = {"semantic": metrics.aggregate(kh_rows_sem),
                  "keyword":  metrics.aggregate(kh_rows_kw)}
        summary["keyword_heavy"] = {
            "n_queries": len(kh_queries),
            "aggregate": kh_agg,
            "per_query": kh_per_query,
        }
        print(f"\n=== KEYWORD-HEAVY BREAKOUT (over {len(kh_queries)} queries) ===", flush=True)
        print("method    " + "  ".join(f"{m:>7}" for m in metrics.METRIC_NAMES))
        for method in ("semantic", "keyword"):
            print(f"{method:<9} " + "  ".join(f"{kh_agg[method][m]:7.3f}" for m in metrics.METRIC_NAMES))

    # ---------------- write versioned artifacts ----------------
    v = next_version("results_raw", ".jsonl")
    raw_path = EVAL_DIR / f"results_raw_v{v}.jsonl"
    with raw_path.open("w") as f:
        for rec in raw_records:
            f.write(json.dumps(rec) + "\n")

    csv_path = EVAL_DIR / f"metrics_summary_v{v}.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["method", "scope", "n_queries"] + metrics.METRIC_NAMES)
        for method in ("semantic", "keyword"):
            w.writerow([method, "overall", len(answerable)]
                       + [round(agg[method][m], 4) for m in metrics.METRIC_NAMES])
        for topic in sorted(per_topic):
            for method in ("semantic", "keyword"):
                w.writerow([method, f"topic:{topic}", per_topic[topic]["n"]]
                           + [round(per_topic[topic][method][m], 4) for m in metrics.METRIC_NAMES])

    json_path = EVAL_DIR / f"summary_v{v}.json"
    json_path.write_text(json.dumps(summary, indent=2))

    tables_path = EVAL_DIR / f"tables_v{v}.md"
    tables_path.write_text(render_tables(summary))

    print(f"\n=== AGGREGATE (over {len(answerable)} answerable queries) ===", flush=True)
    hdr = "method    " + "  ".join(f"{m:>7}" for m in metrics.METRIC_NAMES)
    print(hdr)
    for method in ("semantic", "keyword"):
        print(f"{method:<9} " + "  ".join(f"{agg[method][m]:7.3f}" for m in metrics.METRIC_NAMES))
    print(f"\nwrote {raw_path.name}, {csv_path.name}, {json_path.name}, {tables_path.name}")
    return 0


def render_tables(summary: dict) -> str:
    M = metrics.METRIC_NAMES
    lines: List[str] = []
    lines.append("# Eval tables (auto-generated)\n")
    lines.append(f"Corpus: {summary['n_sessions']} sessions "
                 f"({summary['n_labeled']} labeled + {summary['n_distractor']} distractor). "
                 f"Queries: {summary['n_answerable']} answerable + {summary['n_null']} null. "
                 f"Model: `{summary['model']}` ({summary['embedding_dim']}-dim).\n")

    lines.append("\n## Aggregate: semantic vs keyword\n")
    lines.append("| Method | " + " | ".join(M) + " |")
    lines.append("|---|" + "|".join(["---:"] * len(M)) + "|")
    for method in ("semantic", "keyword"):
        lines.append("| " + method + " | " + " | ".join(f"{summary['aggregate'][method][m]:.3f}" for m in M) + " |")

    lines.append("\n## Per-topic (semantic / keyword)\n")
    lines.append("| Topic | n | " + " | ".join(M) + " |")
    lines.append("|---|--:|" + "|".join(["---:"] * len(M)) + "|")
    for topic in sorted(summary["per_topic"]):
        pt = summary["per_topic"][topic]
        sem = " | ".join(f"{pt['semantic'][m]:.2f}" for m in M)
        lines.append(f"| {topic} (sem) | {pt['n']} | " + sem + " |")
        kw = " | ".join(f"{pt['keyword'][m]:.2f}" for m in M)
        lines.append(f"| {topic} (kw) | {pt['n']} | " + kw + " |")

    lines.append("\n## Per-query (answerable): semantic rank & top-3 vs keyword rank\n")
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

    lines.append("\n## Null queries (no correct session): top-1 returned\n")
    lines.append("| Query | Sem top-1 (id:score) | KW top-1 (id:score) |")
    lines.append("|---|---|---|")
    for p in summary["per_query"]:
        if p["gold"] is not None:
            continue
        q = p["query"] if len(p["query"]) <= 70 else p["query"][:67] + "..."
        st = p["semantic"]["top1"]
        kt = p["keyword"]["top1"]
        lines.append(f"| {q} | {st[0]}:{st[1]} | {kt[0]}:{kt[1]} |")

    if "keyword_heavy" in summary:
        kh = summary["keyword_heavy"]
        lines.append("\n## Keyword-heavy queries breakout (exact tool names / flags)\n")
        lines.append(f"*{kh['n_queries']} queries using exact keywords from target sessions "
                     f"(opposite of the standard eval design). "
                     f"Reported separately — not merged into the answerable aggregate.*\n")
        lines.append("| Method | " + " | ".join(M) + " |")
        lines.append("|---|" + "|".join(["---:"] * len(M)) + "|")
        for method in ("semantic", "keyword"):
            lines.append("| " + method + " | "
                         + " | ".join(f"{kh['aggregate'][method][m]:.3f}" for m in M) + " |")
        lines.append("\n| Query | Expected | Sem rank | Sem top-3 (id:score) | KW rank |")
        lines.append("|---|---|--:|---|--:|")
        for p in kh["per_query"]:
            q = p["query"] if len(p["query"]) <= 70 else p["query"][:67] + "..."
            sem_r = p["semantic"]["rank"] if p["semantic"]["rank"] else "NF"
            kw_r  = p["keyword"]["rank"]  if p["keyword"]["rank"]  else "NF"
            top3  = "<br>".join(f"{sid}:{sc}" for sid, sc in p["semantic"]["top3"])
            lines.append(f"| {q} | {p['gold']} | {sem_r} | {top3} | {kw_r} |")

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(run())
