"""Tests for hist.embedder.

Runs fully offline against the locally cached
sentence-transformers/all-MiniLM-L6-v2 model. Make sure HF_HUB_OFFLINE=1 and
TRANSFORMERS_OFFLINE=1 are set in the environment before invoking pytest.
"""

from __future__ import annotations

import numpy as np
import pytest

from hist.config import Config
from hist.embedder import FastEmbedEmbedder, build_embedder
from hist.interfaces import Embedder


@pytest.fixture(scope="module")
def embedder() -> FastEmbedEmbedder:
    return FastEmbedEmbedder()


def test_encode_shape_and_dtype(embedder: FastEmbedEmbedder) -> None:
    vectors = embedder.encode(["a", "b"])

    assert vectors.shape == (2, 384)
    assert vectors.dtype == np.float32


def test_encode_rows_are_unit_normalized(embedder: FastEmbedEmbedder) -> None:
    vectors = embedder.encode(["a", "b"])
    norms = np.linalg.norm(vectors, axis=1)

    assert np.allclose(norms, 1.0, atol=1e-5)


def test_encode_empty_input(embedder: FastEmbedEmbedder) -> None:
    vectors = embedder.encode([])

    assert vectors.shape == (0, 384)
    assert vectors.dtype == np.float32


def test_encode_one_matches_encode(embedder: FastEmbedEmbedder) -> None:
    one = embedder.encode_one("hello world")
    batch = embedder.encode(["hello world"])

    assert one.shape == (384,)
    assert np.allclose(one, batch[0])


def test_semantic_similarity_sanity_check(embedder: FastEmbedEmbedder) -> None:
    query = embedder.encode_one("systemctl reload nginx")
    related = embedder.encode_one("restart the nginx web server")
    unrelated = embedder.encode_one("postgres database backup")

    cosine_related = float(np.dot(query, related))
    cosine_unrelated = float(np.dot(query, unrelated))

    assert cosine_related > cosine_unrelated


def test_dim_property(embedder: FastEmbedEmbedder) -> None:
    assert embedder.dim == 384


def test_is_embedder_subclass(embedder: FastEmbedEmbedder) -> None:
    assert isinstance(embedder, Embedder)


def test_build_embedder_uses_config_defaults() -> None:
    config = Config.default()
    built = build_embedder(config)

    assert isinstance(built, Embedder)
    assert built.dim == config.embedding_dim


def test_lazy_load_does_not_load_model_on_init() -> None:
    e = FastEmbedEmbedder()

    assert e._model is None
