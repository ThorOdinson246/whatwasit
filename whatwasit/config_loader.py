"""Load user overrides from ``~/.config/whatwasit/config.toml`` (XDG).

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
_VALID_TUI_THEMES = frozenset({"midnight", "default", "high-contrast"})


def _xdg_config_home() -> Path:
    env = os.environ.get("XDG_CONFIG_HOME")
    if env:
        return Path(env)
    return Path.home() / ".config"


from .brand import resolve_config_file


def config_file_path() -> Path:
    """Return the XDG path for the whatwasit config file."""
    return resolve_config_file(_xdg_config_home())


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

    if "tui_theme" in data:
        theme = str(data["tui_theme"]).lower()
        if theme in _VALID_TUI_THEMES:
            config.tui_theme = theme

    return config


def save_config_value(key: str, value: object) -> None:
    """Persist a single config key to the user's TOML file."""
    path = config_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = dict(load_config_file())
    data[key] = value
    lines: list[str] = []
    for k, v in sorted(data.items()):
        if isinstance(v, bool):
            lines.append(f"{k} = {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k} = {v}")
        else:
            escaped = str(v).replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{k} = "{escaped}"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
