"""Named eval-suite registry."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class EvalSuite:
    name: str
    sessions_path: Path
    queries_path: Path
    label: str
    include_in_canonical: bool = False

    def exists(self) -> bool:
        return self.sessions_path.exists() and self.queries_path.exists()


SUITES: dict[str, EvalSuite] = {
    "standard": EvalSuite(
        name="standard",
        sessions_path=EVAL_DIR / "sessions.jsonl",
        queries_path=EVAL_DIR / "queries.jsonl",
        label="Standard intent paraphrase suite",
        include_in_canonical=True,
    ),
    "keyword_heavy": EvalSuite(
        name="keyword_heavy",
        sessions_path=EVAL_DIR / "sessions.jsonl",
        queries_path=EVAL_DIR / "queries_keyword_heavy.jsonl",
        label="Keyword-heavy exact tool/flag suite",
    ),
    "hard": EvalSuite(
        name="hard",
        sessions_path=EVAL_DIR / "hard_sessions.jsonl",
        queries_path=EVAL_DIR / "hard_queries.jsonl",
        label="Hard confusable/noisy/error suite",
    ),
    "raw_noise": EvalSuite(
        name="raw_noise",
        sessions_path=EVAL_DIR / "raw_noise_sessions.jsonl",
        queries_path=EVAL_DIR / "raw_noise_queries.jsonl",
        label="External raw-command stress suite",
    ),
    "personal": EvalSuite(
        name="personal",
        sessions_path=EVAL_DIR / "private" / "personal" / "sessions.jsonl",
        queries_path=EVAL_DIR / "private" / "personal" / "queries.jsonl",
        label="Private personal recall suite",
    ),
}


def available_suites() -> dict[str, EvalSuite]:
    return {name: suite for name, suite in SUITES.items() if suite.exists()}


def get_suite(name: str) -> EvalSuite:
    try:
        suite = SUITES[name]
    except KeyError as exc:
        known = ", ".join(sorted(SUITES))
        raise SystemExit(f"unknown suite {name!r}; known suites: {known}") from exc
    if not suite.exists():
        raise SystemExit(f"suite {name!r} is missing {suite.sessions_path} or {suite.queries_path}")
    return suite
