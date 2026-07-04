from __future__ import annotations

import pytest

from eval.run_eval import parse_args, resolve_retrieval_limit, selected_suites
from whatwasit.config import Config


def test_default_selection_preserves_standard_and_keyword_heavy() -> None:
    args = parse_args([])
    names = [suite.name for suite in selected_suites(args)]
    assert names == ["standard", "keyword_heavy"]


def test_suite_selection_can_target_hard_suite() -> None:
    args = parse_args(["--suite", "hard"])
    assert [suite.name for suite in selected_suites(args)] == ["hard"]


def test_all_suites_includes_available_named_suites() -> None:
    args = parse_args(["--all-suites"])
    names = {suite.name for suite in selected_suites(args)}
    assert {"standard", "keyword_heavy", "hard"} <= names


def test_retrieval_k_modes() -> None:
    config = Config(top_k=7)
    assert resolve_retrieval_limit("full", config, 42) == (42, "full")
    assert resolve_retrieval_limit("production", config, 42) == (7, "production")
    assert resolve_retrieval_limit("3", config, 42) == (3, "3")


def test_retrieval_k_rejects_invalid_values() -> None:
    config = Config()
    with pytest.raises(SystemExit):
        resolve_retrieval_limit("nope", config, 42)
    with pytest.raises(SystemExit):
        resolve_retrieval_limit("0", config, 42)
