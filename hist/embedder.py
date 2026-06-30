"""FastEmbed-backed implementation of the :class:`Embedder` interface.

Uses ``fastembed.TextEmbedding`` to run a small ONNX sentence-transformer
model fully offline (no torch, no GPU required). The underlying model is
loaded lazily on first use so importing this module and constructing an
embedder stays cheap.
"""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np

from hist.config import Config
from hist.interfaces import Embedder


class FastEmbedEmbedder(Embedder):
    """Embeds text using a fastembed ``TextEmbedding`` model."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        dim: int = 384,
        cache_dir: Optional[str] = None,
    ) -> None:
        self._model_name = model_name
        self._dim = dim
        self._cache_dir = cache_dir
        self._model = None

    @property
    def dim(self) -> int:
        return self._dim

    def _ensure_model(self):
        if self._model is None:
            from fastembed import TextEmbedding

            self._model = TextEmbedding(
                model_name=self._model_name,
                cache_dir=self._cache_dir,
            )
        return self._model

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        texts = list(texts)
        if not texts:
            return np.empty((0, self._dim), dtype=np.float32)

        model = self._ensure_model()
        vectors = np.asarray(list(model.embed(texts)), dtype=np.float32)

        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        vectors = vectors / norms

        return vectors.astype(np.float32)


def build_embedder(config: Config) -> Embedder:
    """Construct the configured :class:`Embedder` implementation."""
    return FastEmbedEmbedder(
        model_name=config.model_name,
        dim=config.embedding_dim,
    )
