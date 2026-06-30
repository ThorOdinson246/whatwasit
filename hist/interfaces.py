"""Thin abstract interfaces for the swappable subsystems.

The embedding model and the vector store are both hidden behind these ABCs so
they can be replaced (a different model, hnswlib/sqlite-vec instead of usearch)
without touching the indexer, search, or CLI layers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Sequence, Tuple

import numpy as np


class Embedder(ABC):
    """Turns text into dense vectors. Implementations must run fully offline."""

    @property
    @abstractmethod
    def dim(self) -> int:
        """Dimensionality of the produced vectors."""

    @abstractmethod
    def encode(self, texts: Sequence[str]) -> np.ndarray:
        """Encode a batch of texts.

        Returns a float32 array of shape ``(len(texts), dim)``. Implementations
        should L2-normalize rows so callers can use dot product as cosine
        similarity.
        """

    def encode_one(self, text: str) -> np.ndarray:
        """Convenience: encode a single string into a 1-D ``(dim,)`` vector."""
        return self.encode([text])[0]


class VectorIndex(ABC):
    """A nearest-neighbour index keyed by integer session ids."""

    @abstractmethod
    def add(self, keys: Sequence[int], vectors: np.ndarray) -> None:
        """Add vectors (shape ``(n, dim)``) under the given integer keys."""

    @abstractmethod
    def search(self, vector: np.ndarray, k: int) -> List[Tuple[int, float]]:
        """Return up to ``k`` ``(key, score)`` pairs, best first.

        ``score`` is a similarity where higher means more relevant.
        """

    @abstractmethod
    def save(self) -> None:
        """Persist the index to disk."""

    @abstractmethod
    def load(self) -> None:
        """Load the index from disk if it exists; otherwise start empty."""

    @abstractmethod
    def __len__(self) -> int:
        """Number of vectors currently in the index."""
