"""Single source of truth for product naming and on-disk identifiers."""

from __future__ import annotations

from pathlib import Path

APP_NAME = "whatwasit"
CLI_NAME = "whatwasit"
PYPI_NAME = "whatwasit"
GITHUB_REPO = "whatwasit"

# Pre-rename install used ``hist`` as the internal app id.
LEGACY_APP_NAME = "hist"
LEGACY_DB_FILENAME = "whatwasit.db"
LEGACY_SOCKET_FILENAME = "whatwasit.sock"

DB_FILENAME = f"{APP_NAME}.db"
SOCKET_FILENAME = f"{APP_NAME}.sock"
PID_FILENAME = "daemon.pid"
CONFIG_FILENAME = "config.toml"


def data_dir_name_candidates() -> tuple[str, ...]:
    """Preferred data directory names, newest first."""
    return (APP_NAME, LEGACY_APP_NAME)


def config_dir_name_candidates() -> tuple[str, ...]:
    """Preferred config directory names, newest first."""
    return (APP_NAME, LEGACY_APP_NAME)


def resolve_data_dir(xdg_data_home: Path) -> Path:
    """Pick data dir: prefer new name, fall back to legacy if indexed there."""
    for name in data_dir_name_candidates():
        candidate = xdg_data_home / name
        if (candidate / DB_FILENAME).is_file() or (candidate / LEGACY_DB_FILENAME).is_file():
            return candidate
    return xdg_data_home / APP_NAME


def resolve_config_file(xdg_config_home: Path) -> Path:
    """Pick config file path: prefer new, fall back to legacy if present."""
    for name in config_dir_name_candidates():
        path = xdg_config_home / name / CONFIG_FILENAME
        if path.is_file():
            return path
    return xdg_config_home / APP_NAME / CONFIG_FILENAME


def resolve_db_path(data_dir: Path) -> Path:
    """Return the SQLite path, preferring the new filename when both exist."""
    primary = data_dir / DB_FILENAME
    legacy = data_dir / LEGACY_DB_FILENAME
    if primary.is_file():
        return primary
    if legacy.is_file():
        return legacy
    return primary
