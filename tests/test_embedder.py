"""Tests for hist.embedder.

Runs fully offline against the locally cached
sentence-transformers/all-MiniLM-L6-v2 model. Make sure HF_HUB_OFFLINE=1 and
TRANSFORMERS_OFFLINE=1 are set in the environment before invoking pytest.
"""

from __future__ import annotations

import numpy as np
import pytest

from hist.config import Config
from hist.embedder import (
    AsymmetricOnnxEmbedder,
    FastEmbedEmbedder,
    OnnxEmbedder,
    build_embedder,
)
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

    assert isinstance(built, OnnxEmbedder)
    assert not isinstance(built, AsymmetricOnnxEmbedder)
    assert built.dim == config.embedding_dim


def test_build_embedder_symmetric_for_minilm() -> None:
    config = Config.default()
    config.model_name = "sentence-transformers/all-MiniLM-L6-v2"
    built = build_embedder(config)

    assert isinstance(built, OnnxEmbedder)
    assert not isinstance(built, AsymmetricOnnxEmbedder)


@pytest.fixture(scope="module")
def asymmetric_embedder() -> AsymmetricOnnxEmbedder:
    return AsymmetricOnnxEmbedder(
        model_name="BAAI/bge-small-en-v1.5",
        query_prefix="Represent this sentence for searching relevant passages: ",
    )


def test_asymmetric_query_differs_from_passage(asymmetric_embedder: AsymmetricOnnxEmbedder) -> None:
    text = "reload nginx configuration"
    q = asymmetric_embedder.encode_query([text])[0]
    p = asymmetric_embedder.encode_passage([text])[0]

    assert not np.allclose(q, p)


def test_asymmetric_encode_defaults_to_passage(asymmetric_embedder: AsymmetricOnnxEmbedder) -> None:
    text = "systemctl restart nginx"
    batch = asymmetric_embedder.encode([text])
    passage = asymmetric_embedder.encode_passage([text])

    assert np.allclose(batch, passage)


def test_lazy_load_does_not_load_model_on_init() -> None:
    e = FastEmbedEmbedder()

    # The ONNX session and tokenizer are only built on first encode().
    assert e._session is None
    assert e._tokenizer is None


def test_cached_model_dir_skips_snapshot_download(tmp_path, monkeypatch) -> None:
    """When model.json points at valid ONNX files, no hub download runs."""
    model_dir = tmp_path / "onnx"
    model_dir.mkdir()
    (model_dir / "tokenizer.json").write_text('{"version":"1.0","truncation":null,"padding":null,"added_tokens":[],"normalizer":null,"pre_tokenizer":null,"post_processor":null,"decoder":null,"model":{"type":"WordPiece","unk_token":"[UNK]","continuing_subword_prefix":"##","max_input_chars_per_word":100,"vocab":{}}}', encoding="utf-8")
    (model_dir / "model.onnx").write_bytes(b"\x00")

    from hist import embedder as emb_mod

    emb_mod.persist_model_dir(tmp_path, emb_mod._ONNX_REPOS["sentence-transformers/all-MiniLM-L6-v2"], str(model_dir))

    called = {"n": 0}

    def fake_snapshot_download(*args, **kwargs):
        called["n"] += 1
        return str(model_dir)

    monkeypatch.setattr("huggingface_hub.snapshot_download", fake_snapshot_download)

    e = FastEmbedEmbedder(data_dir=tmp_path)
    resolved = e._resolve_model_dir()

    assert resolved == str(model_dir)
    assert called["n"] == 0


def test_resolve_model_dir_persists_after_hub_download(tmp_path, monkeypatch) -> None:
    model_dir = tmp_path / "hub-cache"
    model_dir.mkdir()
    (model_dir / "tokenizer.json").write_text('{"version":"1.0","truncation":null,"padding":null,"added_tokens":[],"normalizer":null,"pre_tokenizer":null,"post_processor":null,"decoder":null,"model":{"type":"WordPiece","unk_token":"[UNK]","continuing_subword_prefix":"##","max_input_chars_per_word":100,"vocab":{}}}', encoding="utf-8")
    (model_dir / "model.onnx").write_bytes(b"\x00")

    def fake_snapshot_download(*args, **kwargs):
        return str(model_dir)

    monkeypatch.setattr("huggingface_hub.snapshot_download", fake_snapshot_download)

    e = FastEmbedEmbedder(data_dir=tmp_path)
    resolved = e._resolve_model_dir()

    assert resolved == str(model_dir)
    assert (tmp_path / "model.json").is_file()
    assert emb_mod_load_cached(tmp_path) == str(model_dir)


def emb_mod_load_cached(tmp_path):
    from hist.embedder import _ONNX_REPOS, load_cached_model_dir

    return load_cached_model_dir(tmp_path, _ONNX_REPOS["sentence-transformers/all-MiniLM-L6-v2"])
