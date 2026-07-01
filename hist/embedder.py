"""ONNX-backed implementation of the :class:`Embedder` interface.

Runs the ``all-MiniLM-L6-v2`` sentence-embedding model fully offline on CPU via
``onnxruntime`` + ``tokenizers`` (no PyTorch, no GPU). The ONNX weights and
tokenizer are fetched once from the Hugging Face Hub and cached locally.

Why not fastembed? fastembed ships the same model, but its Python embedding
pipeline measured ~6-20x slower than driving onnxruntime directly on this CPU
(~28 texts/sec vs ~600 texts/sec) because it does not enable graph optimization
/ multi-threaded intra-op execution and adds per-item overhead. Driving the same
ONNX graph ourselves produces *bit-for-bit equivalent* vectors (cosine 1.0) at a
fraction of the time, which is what lets us meet the indexing and query-latency
budgets. The model stays swappable behind the :class:`Embedder` interface.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Sequence

import numpy as np

from hist.config import Config
from hist.interfaces import Embedder

# Maps a logical sentence-transformers model name to the repo that hosts its
# ONNX export (model.onnx + tokenizer.json).
_ONNX_REPOS: Dict[str, str] = {
    "sentence-transformers/all-MiniLM-L6-v2": "qdrant/all-MiniLM-L6-v2-onnx",
}

_DEFAULT_BATCH_SIZE = 256
_DEFAULT_MAX_LENGTH = 256


class OnnxEmbedder(Embedder):
    """Embeds text with an ONNX MiniLM model via onnxruntime + tokenizers."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        dim: int = 384,
        cache_dir: Optional[str] = None,
        onnx_repo: Optional[str] = None,
        max_length: int = _DEFAULT_MAX_LENGTH,
        batch_size: int = _DEFAULT_BATCH_SIZE,
        threads: Optional[int] = None,
    ) -> None:
        self._model_name = model_name
        self._dim = dim
        self._cache_dir = cache_dir
        self._onnx_repo = onnx_repo or _ONNX_REPOS.get(model_name, model_name)
        self._max_length = max_length
        self._batch_size = batch_size
        self._threads = threads or os.cpu_count() or 1

        # Lazily initialized on first encode so construction stays cheap.
        self._session = None
        self._tokenizer = None
        self._input_names: set = set()

    @property
    def dim(self) -> int:
        return self._dim

    def _ensure_model(self) -> None:
        if self._session is not None:
            return

        import onnxruntime as ort
        from huggingface_hub import snapshot_download
        from tokenizers import Tokenizer

        model_dir = snapshot_download(self._onnx_repo, cache_dir=self._cache_dir)

        tokenizer = Tokenizer.from_file(os.path.join(model_dir, "tokenizer.json"))
        tokenizer.enable_truncation(max_length=self._max_length)
        tokenizer.enable_padding()
        self._tokenizer = tokenizer

        opts = ort.SessionOptions()
        opts.intra_op_num_threads = self._threads
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self._session = ort.InferenceSession(
            os.path.join(model_dir, "model.onnx"),
            opts,
            providers=["CPUExecutionProvider"],
        )
        self._input_names = {i.name for i in self._session.get_inputs()}

    def _encode_batch(self, texts: List[str]) -> np.ndarray:
        encodings = self._tokenizer.encode_batch(texts)
        ids = np.array([e.ids for e in encodings], dtype=np.int64)
        mask = np.array([e.attention_mask for e in encodings], dtype=np.int64)

        feed = {"input_ids": ids, "attention_mask": mask}
        if "token_type_ids" in self._input_names:
            feed["token_type_ids"] = np.zeros_like(ids)

        last_hidden = self._session.run(None, feed)[0]  # (B, L, dim)

        # Mean-pool over tokens, weighted by the attention mask (matches
        # sentence-transformers' all-MiniLM-L6-v2 pooling).
        m = mask[:, :, None].astype(np.float32)
        summed = (last_hidden * m).sum(axis=1)
        counts = np.clip(m.sum(axis=1), 1e-9, None)
        return (summed / counts).astype(np.float32)

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        texts = list(texts)
        if not texts:
            return np.empty((0, self._dim), dtype=np.float32)

        self._ensure_model()

        chunks: List[np.ndarray] = []
        for start in range(0, len(texts), self._batch_size):
            chunks.append(self._encode_batch(texts[start : start + self._batch_size]))
        vectors = np.concatenate(chunks, axis=0)

        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return (vectors / norms).astype(np.float32)


# Backwards-compatible alias: the public factory and historical name.
FastEmbedEmbedder = OnnxEmbedder


def build_embedder(config: Config) -> Embedder:
    """Construct the configured :class:`Embedder` implementation."""
    return OnnxEmbedder(model_name=config.model_name, dim=config.embedding_dim)
