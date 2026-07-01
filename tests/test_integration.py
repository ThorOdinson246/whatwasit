"""End-to-end integration test.

Generates a synthetic shell history with several distinct topic sessions
(nginx / docker / postgres / git-rebase / python-venv), indexes it with the
*real* embedder, then runs a natural-language query for each topic and asserts
the correct session comes back in the top 3 results.

Uses the local ONNX BGE model from cache; runs fully offline.
"""

from __future__ import annotations

import os

# Force fully-offline model loading before fastembed is imported anywhere.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import pytest

from hist.config import Config
from hist.embedder import build_embedder
from hist.index import build_index
from hist.indexer import index_commands
from hist.parsers.zsh import parse_zsh
from hist.search import search
from tests import synthetic

# A signature substring that appears only in each topic's commands, used to
# locate that topic's session among the grouped sessions.
TOPIC_SIGNATURES = {
    "nginx": "nginx -t",
    "docker": "docker network create",
    "postgres": "pg_hba.conf",
    "git-rebase": "git rebase -i",
    "python-venv": "python3 -m venv",
}


@pytest.fixture(scope="module")
def indexed(tmp_path_factory):
    """Build a real on-disk index from synthetic history once for all queries."""
    data_dir = tmp_path_factory.mktemp("histdata")
    hist_file = data_dir / "synthetic_zsh_history"
    synthetic.write_zsh_history(str(hist_file), seed=7)

    config = Config(data_dir=data_dir)
    commands = parse_zsh(str(hist_file))
    assert commands, "parser produced no commands"

    embedder = build_embedder(config)
    index = build_index(config)
    stats = index_commands(config, commands, embedder=embedder, index=index, reset=True)

    # One session per topic (topics are separated by a >5min gap).
    assert stats.n_sessions == len(synthetic.TOPICS)
    return config


def _session_signature_topic(doc_text: str) -> str | None:
    for topic, sig in TOPIC_SIGNATURES.items():
        if sig in doc_text:
            return topic
    return None


@pytest.mark.parametrize("topic", list(TOPIC_SIGNATURES))
def test_query_returns_correct_session_top3(indexed, topic):
    config = indexed
    query = synthetic.TOPIC_QUERIES[topic]

    results = search(config, query, k=3)
    assert results, f"no results for query: {query!r}"

    top_topics = [_session_signature_topic(r.session.to_document()) for r in results[:3]]
    assert topic in top_topics, (
        f"query {query!r} expected topic {topic!r} in top-3, got {top_topics}"
    )


def test_top1_accuracy_is_high(indexed):
    """The correct topic should also rank #1 for most queries (sanity on quality)."""
    config = indexed
    top1_hits = 0
    for topic, query in synthetic.TOPIC_QUERIES.items():
        results = search(config, query, k=5)
        assert results
        if _session_signature_topic(results[0].session.to_document()) == topic:
            top1_hits += 1
    # Allow one miss across the topics; the rest must be exact #1.
    assert top1_hits >= len(synthetic.TOPIC_QUERIES) - 1


def test_matched_indices_are_populated(indexed):
    config = indexed
    results = search(config, synthetic.TOPIC_QUERIES["nginx"], k=3)
    assert results[0].matched_indices, "expected highlighted matched commands"
