"""Emit reproducible eval commands for local accuracy experiments.

This module intentionally does not change search behavior. It gives experiment
branches a shared command matrix so results can be compared consistently.
"""

from __future__ import annotations

import argparse
import shlex
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Experiment:
    name: str
    suite: str
    retrieval_k: str
    model_name: str
    embedding_dim: int
    ranking_variant: str

    def command(self) -> str:
        args = [
            "HF_HUB_OFFLINE=1",
            "TRANSFORMERS_OFFLINE=1",
            "python",
            "eval/run_eval.py",
            "--suite",
            self.suite,
            "--retrieval-k",
            self.retrieval_k,
            "--model-name",
            self.model_name,
            "--embedding-dim",
            str(self.embedding_dim),
            "--ranking-variant",
            self.ranking_variant,
        ]
        return " ".join(shlex.quote(arg) for arg in args)


MINILM = "sentence-transformers/all-MiniLM-L6-v2"
BGE = "BAAI/bge-small-en-v1.5"


EXPERIMENTS: list[Experiment] = [
    Experiment("minilm-standard-full", "standard", "full", MINILM, 384, "production"),
    Experiment("minilm-standard-production", "standard", "production", MINILM, 384, "production"),
    Experiment("minilm-hard-production", "hard", "production", MINILM, 384, "production"),
    Experiment("minilm-hard-full", "hard", "full", MINILM, 384, "production"),
    Experiment("bge-hard-production", "hard", "production", BGE, 384, "bge-small-eval"),
    Experiment("bge-standard-production", "standard", "production", BGE, 384, "bge-small-eval"),
]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="List experiment names")
    parser.add_argument("--name", action="append", help="Emit only selected experiment name")
    return parser.parse_args(argv)


def selected(names: Sequence[str] | None) -> list[Experiment]:
    if not names:
        return EXPERIMENTS
    wanted = set(names)
    found = [exp for exp in EXPERIMENTS if exp.name in wanted]
    missing = wanted - {exp.name for exp in found}
    if missing:
        raise SystemExit(f"unknown experiments: {', '.join(sorted(missing))}")
    return found


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    experiments = selected(args.name)
    if args.list:
        for exp in experiments:
            print(exp.name)
    else:
        for exp in experiments:
            print(f"# {exp.name}")
            print(exp.command())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
