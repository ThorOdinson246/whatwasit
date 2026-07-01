"""Load user overrides from ``~/.config/hist/config.toml`` (XDG).

Uses :mod:`tomllib` on Python 3.11+ and :mod:`tomli` on 3.9–3.10.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[no-redef]

if TYPE_CHECKING:
    from .config import Config

_VALID_OUTPUT_MODES = frozenset({"tui", "plain"})


def _xdg_config_home() -> Path:
    env = os.environ.get("XDG_CONFIG_HOME")
    if env:
        return Path(env)
    return Path.home() / ".config"


def config_file_path() -> Path:
    """Return the XDG path for the hist config file."""
    return _xdg_config_home() / "hist" / "config.toml"


def load_config_file() -> Mapping[str, Any]:
    """Parse the config file if it exists; otherwise return an empty mapping."""
    path = config_file_path()
    if not path.is_file():
        return {}
    with path.open("rb") as handle:
        return tomllib.load(handle)


def apply_file_overrides(config: "Config") -> "Config":
    """Apply values from the on-disk config file onto *config*.

    Unknown keys are ignored. Invalid ``output_mode`` values are skipped so
    defaults remain in effect.
    """
    data = load_config_file()
    if not data:
        return config

    if "output_mode" in data:
        mode = str(data["output_mode"]).lower()
        if mode in _VALID_OUTPUT_MODES:
            config.output_mode = mode

    if "tui_page_size" in data:
        try:
            config.tui_page_size = int(data["tui_page_size"])
        except (TypeError, ValueError):
            pass

    if "low_confidence_threshold" in data:
        try:
            config.low_confidence_threshold = float(data["low_confidence_threshold"])
        except (TypeError, ValueError):
            pass

    if "use_daemon" in data:
        config.use_daemon = bool(data["use_daemon"])

    return config
