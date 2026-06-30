"""usearch-backed implementation of :class:`hist.interfaces.VectorIndex`."""

from __future__ import annotations

from pathlib import Path
from typing import List, Sequence, Tuple, Union

import numpy as np
from usearch.index import Index

from hist.config import Config
from hist.interfaces import VectorIndex


class UsearchIndex(VectorIndex):
    """Approximate nearest-neighbour index backed by ``usearch``."""

    def __init__(self, path: Union[str, Path], dim: int, metric: str = "cos") -> None:
        self.path = Path(path)
        self.dim = dim
        self.metric = metric
        self._index = Index(ndim=dim, metric=metric, dtype="f32")

    def add(self, keys: Sequence[int], vectors: np.ndarray) -> None:
        keys_arr = np.asarray(keys, dtype=np.int64)
        vectors_arr = np.asarray(vectors, dtype=np.float32)
        if vectors_arr.ndim == 1:
            vectors_arr = vectors_arr.reshape(1, -1)
        self._index.add(keys_arr, vectors_arr)

    def search(self, vector: np.ndarray, k: int) -> List[Tuple[int, float]]:
        vector_arr = np.asarray(vector, dtype=np.float32)
        if vector_arr.ndim == 2:
            vector_arr = vector_arr.reshape(-1)
        matches = self._index.search(vector_arr, k)
        results = [
            (int(key), 1.0 - float(distance))
            for key, distance in zip(matches.keys, matches.distances)
        ]
        results.sort(key=lambda pair: pair[1], reverse=True)
        return results[:k]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._index.save(self.path)

    def load(self) -> None:
        if self.path.exists():
            self._index.load(self.path)

    def __len__(self) -> int:
        return len(self._index)


def build_index(config: Config) -> VectorIndex:
    """Construct the configured :class:`VectorIndex` implementation."""
    return UsearchIndex(config.index_path, config.embedding_dim)
