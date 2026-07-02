"""Central configuration for whatwasit.

All tunable values (session window, model name, storage paths, schema version)
live here so nothing is scattered across the codebase as magic constants.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .brand import resolve_data_dir, resolve_db_path

SCHEMA_VERSION = 1
"""Bumped whenever the on-disk SQLite schema changes. Stored in the ``meta`` table."""

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_EMBEDDING_DIM = 384
DEFAULT_LOW_CONFIDENCE_THRESHOLD = 0.40
DEFAULT_SESSION_WINDOW_SECONDS = 300  # 5 minutes
DEFAULT_TOP_K = 10


def _xdg_data_home() -> Path:
    env = os.environ.get("XDG_DATA_HOME")
    if env:
        return Path(env)
    return Path.home() / ".local" / "share"


@dataclass
class Config:
    """Runtime configuration. Construct via :meth:`default` then override fields."""

    # Storage
    data_dir: Path = field(default_factory=lambda: resolve_data_dir(_xdg_data_home()))

    # Session grouping
    session_window_seconds: int = DEFAULT_SESSION_WINDOW_SECONDS
    split_on_cwd_change: bool = True

    # Embedding
    model_name: str = DEFAULT_MODEL_NAME
    embedding_dim: int = DEFAULT_EMBEDDING_DIM

    # Search
    top_k: int = DEFAULT_TOP_K
    hybrid_search: bool = True
    low_confidence_threshold: float = DEFAULT_LOW_CONFIDENCE_THRESHOLD

    # Output / TUI
    output_mode: str = "tui"  # "tui" | "plain"
    tui_page_size: int = 5
    use_daemon: bool = True

    # Schema (read-only constant exposed for convenience)
    schema_version: int = SCHEMA_VERSION

    @classmethod
    def default(cls) -> "Config":
        from .config_loader import apply_file_overrides

        return apply_file_overrides(cls())

    @property
    def db_path(self) -> Path:
        return resolve_db_path(self.data_dir)

    @property
    def index_path(self) -> Path:
        return self.data_dir / "index.usearch"

    def ensure_data_dir(self) -> Path:
        """Create the data directory if it does not yet exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return self.data_dir

    def to_dict(self) -> dict:
        d = asdict(self)
        d["data_dir"] = str(self.data_dir)
        return d
