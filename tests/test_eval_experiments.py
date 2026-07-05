from __future__ import annotations

import pytest

from eval.experiments import EXPERIMENTS, selected


def test_experiment_names_are_unique() -> None:
    names = [exp.name for exp in EXPERIMENTS]
    assert len(names) == len(set(names))


def test_experiment_command_records_metadata() -> None:
    exp = selected(["minilm-hard-production"])[0]
    cmd = exp.command()
    assert "--suite hard" in cmd
    assert "--retrieval-k production" in cmd
    assert "--ranking-variant production" in cmd


def test_personal_experiments_are_available() -> None:
    names = {exp.name for exp in EXPERIMENTS}
    assert "minilm-personal-production" in names
    assert "bge-personal-production" in names


def test_unknown_experiment_exits() -> None:
    with pytest.raises(SystemExit):
        selected(["missing"])
