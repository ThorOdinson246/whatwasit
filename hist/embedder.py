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

import json
import os
import time
from pathlib import Path
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
_MODEL_JSON = "model.json"
_META_ONNX_MODEL_DIR = "onnx_model_dir"


def _is_valid_model_dir(path: Path | str) -> bool:
    p = Path(path)
    return (p / "tokenizer.json").is_file() and (p / "model.onnx").is_file()


def _model_cache_path(data_dir: Path) -> Path:
    return data_dir / _MODEL_JSON


def load_cached_model_dir(data_dir: Path, onnx_repo: str) -> Optional[str]:
    """Return a persisted ONNX model directory when files are present on disk."""
    sidecar = _model_cache_path(data_dir)
    if sidecar.is_file():
        try:
            data = json.loads(sidecar.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
        if data.get("onnx_repo") == onnx_repo:
            model_dir = data.get("model_dir")
            if model_dir and _is_valid_model_dir(model_dir):
                return str(model_dir)

    db_path = data_dir / "hist.db"
    if db_path.is_file():
        from hist import db

        conn = db.connect(db_path)
        try:
            has_meta = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'meta'"
            ).fetchone()
            if has_meta:
                model_dir = db.get_meta(conn, _META_ONNX_MODEL_DIR)
                if model_dir and _is_valid_model_dir(model_dir):
                    return model_dir
        finally:
            conn.close()
    return None


def persist_model_dir(data_dir: Path, onnx_repo: str, model_dir: str) -> None:
    """Record the resolved ONNX model directory in the sidecar cache file."""
    data_dir.mkdir(parents=True, exist_ok=True)
    sidecar = _model_cache_path(data_dir)
    sidecar.write_text(
        json.dumps({"onnx_repo": onnx_repo, "model_dir": model_dir}, indent=2),
        encoding="utf-8",
    )


def sync_model_dir_to_db(conn, model_dir: str) -> None:
    """Persist the ONNX model path into an open SQLite connection's meta table."""
    from hist import db

    db.set_meta(conn, _META_ONNX_MODEL_DIR, model_dir)


def is_model_cached(config: Config) -> bool:
    """True when a persisted ONNX model path exists and is loadable offline."""
    onnx_repo = _ONNX_REPOS.get(config.model_name, config.model_name)
    return load_cached_model_dir(config.data_dir, onnx_repo) is not None


class OnnxEmbedder(Embedder):
    """Embeds text with an ONNX MiniLM model via onnxruntime + tokenizers."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        dim: int = 384,
        cache_dir: Optional[str] = None,
        data_dir: Optional[Path | str] = None,
        onnx_repo: Optional[str] = None,
        max_length: int = _DEFAULT_MAX_LENGTH,
        batch_size: int = _DEFAULT_BATCH_SIZE,
        threads: Optional[int] = None,
    ) -> None:
        self._model_name = model_name
        self._dim = dim
        self._cache_dir = cache_dir
        self._data_dir = Path(data_dir) if data_dir is not None else None
        self._onnx_repo = onnx_repo or _ONNX_REPOS.get(model_name, model_name)
        self._max_length = max_length
        self._batch_size = batch_size
        self._threads = threads or os.cpu_count() or 1

        # Lazily initialized on first encode so construction stays cheap.
        self._session = None
        self._tokenizer = None
        self._input_names: set = set()
        self._model_dir: Optional[str] = None
        self._load_timings: Dict[str, float] = {}

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def model_dir(self) -> Optional[str]:
        """Resolved ONNX asset directory after the first load."""
        return self._model_dir

    @property
    def load_timings(self) -> Dict[str, float]:
        """Seconds spent in each phase of the most recent model load."""
        return dict(self._load_timings)

    def _resolve_model_dir(self) -> str:
        """Locate ONNX assets, downloading only when no valid cache exists."""
        from huggingface_hub import snapshot_download

        if self._data_dir is not None:
            cached = load_cached_model_dir(self._data_dir, self._onnx_repo)
            if cached is not None:
                return cached

        t0 = time.perf_counter()
        try:
            model_dir = snapshot_download(
                self._onnx_repo,
                cache_dir=self._cache_dir,
                local_files_only=True,
            )
        except Exception:
            model_dir = snapshot_download(self._onnx_repo, cache_dir=self._cache_dir)

        if not _is_valid_model_dir(model_dir):
            raise RuntimeError(f"Invalid ONNX model directory: {model_dir}")

        self._load_timings["resolve_dir"] = time.perf_counter() - t0
        self._model_dir = model_dir

        if self._data_dir is not None:
            persist_model_dir(self._data_dir, self._onnx_repo, model_dir)

        return model_dir

    def _ensure_model(self) -> None:
        if self._session is not None:
            return

        import onnxruntime as ort
        from tokenizers import Tokenizer

        t_total = time.perf_counter()
        model_dir = self._resolve_model_dir()

        t0 = time.perf_counter()
        tokenizer = Tokenizer.from_file(os.path.join(model_dir, "tokenizer.json"))
        tokenizer.enable_truncation(max_length=self._max_length)
        tokenizer.enable_padding()
        self._tokenizer = tokenizer
        self._load_timings["load_tokenizer"] = time.perf_counter() - t0

        t0 = time.perf_counter()
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = self._threads
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self._session = ort.InferenceSession(
            os.path.join(model_dir, "model.onnx"),
            opts,
            providers=["CPUExecutionProvider"],
        )
        self._input_names = {i.name for i in self._session.get_inputs()}
        self._load_timings["load_session"] = time.perf_counter() - t0
        self._load_timings["total"] = time.perf_counter() - t_total

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
    return OnnxEmbedder(
        model_name=config.model_name,
        dim=config.embedding_dim,
        data_dir=config.data_dir,
    )
