"""Tests for the usearch-backed VectorIndex implementation."""

from __future__ import annotations

import numpy as np
import pytest

from whatwasit.config import Config
from whatwasit.index import UsearchIndex, build_index

DIM = 32
N = 10


def _make_vectors(n: int, dim: int, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    vecs = rng.standard_normal((n, dim)).astype(np.float32)
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs


def test_search_returns_exact_match_first(tmp_path):
    path = tmp_path / "index.usearch"
    index = UsearchIndex(path, DIM)

    vectors = _make_vectors(N, DIM)
    keys = list(range(100, 100 + N))
    index.add(keys, vectors)

    query_idx = 3
    results = index.search(vectors[query_idx], k=5)

    assert len(results) == 5
    top_key, top_score = results[0]
    assert top_key == keys[query_idx]
    assert top_score == pytest.approx(1.0, abs=1e-4)


def test_results_sorted_descending_by_score(tmp_path):
    path = tmp_path / "index.usearch"
    index = UsearchIndex(path, DIM)

    vectors = _make_vectors(N, DIM)
    keys = list(range(N))
    index.add(keys, vectors)

    results = index.search(vectors[0], k=N)

    assert len(results) == N
    scores = [score for _, score in results]
    assert scores == sorted(scores, reverse=True)


def test_len_reflects_added_vectors(tmp_path):
    path = tmp_path / "index.usearch"
    index = UsearchIndex(path, DIM)

    assert len(index) == 0

    vectors = _make_vectors(N, DIM)
    keys = list(range(N))
    index.add(keys, vectors)

    assert len(index) == N


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "index.usearch"
    index = UsearchIndex(path, DIM)

    vectors = _make_vectors(N, DIM)
    keys = list(range(200, 200 + N))
    index.add(keys, vectors)
    index.save()

    assert path.exists()

    query_idx = 5
    expected_key = keys[query_idx]
    expected_top = index.search(vectors[query_idx], k=1)[0][0]
    assert expected_top == expected_key

    reloaded = UsearchIndex(path, DIM)
    reloaded.load()

    assert len(reloaded) == N
    results = reloaded.search(vectors[query_idx], k=1)
    assert results[0][0] == expected_key


def test_load_without_existing_file_is_noop(tmp_path):
    path = tmp_path / "missing.usearch"
    index = UsearchIndex(path, DIM)

    index.load()

    assert len(index) == 0


def test_build_index_uses_config_path_and_dim(tmp_path):
    config = Config(data_dir=tmp_path)
    index = build_index(config)

    assert isinstance(index, UsearchIndex)
    assert index.path == config.index_path
    assert index.dim == config.embedding_dim
