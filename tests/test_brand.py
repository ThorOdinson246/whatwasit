"""Tests for whatwasit.brand path resolution and legacy hist migration."""

from __future__ import annotations

from pathlib import Path

from whatwasit.brand import (
    LEGACY_APP_NAME,
    LEGACY_DB_FILENAME,
    APP_NAME,
    DB_FILENAME,
    resolve_config_file,
    resolve_data_dir,
    resolve_db_path,
)


def test_resolve_data_dir_prefers_new_when_indexed(tmp_path: Path) -> None:
    new = tmp_path / APP_NAME
    new.mkdir()
    (new / DB_FILENAME).write_text("", encoding="utf-8")
    legacy = tmp_path / LEGACY_APP_NAME
    legacy.mkdir()
    (legacy / LEGACY_DB_FILENAME).write_text("", encoding="utf-8")

    assert resolve_data_dir(tmp_path) == new


def test_resolve_data_dir_falls_back_to_legacy(tmp_path: Path) -> None:
    legacy = tmp_path / LEGACY_APP_NAME
    legacy.mkdir()
    (legacy / LEGACY_DB_FILENAME).write_text("", encoding="utf-8")

    assert resolve_data_dir(tmp_path) == legacy


def test_resolve_data_dir_defaults_to_new(tmp_path: Path) -> None:
    assert resolve_data_dir(tmp_path) == tmp_path / APP_NAME


def test_resolve_db_path_prefers_new_filename(tmp_path: Path) -> None:
    (tmp_path / DB_FILENAME).write_text("", encoding="utf-8")
    (tmp_path / LEGACY_DB_FILENAME).write_text("", encoding="utf-8")
    assert resolve_db_path(tmp_path) == tmp_path / DB_FILENAME


def test_resolve_db_path_uses_legacy_when_only_legacy_exists(tmp_path: Path) -> None:
    (tmp_path / LEGACY_DB_FILENAME).write_text("", encoding="utf-8")
    assert resolve_db_path(tmp_path) == tmp_path / LEGACY_DB_FILENAME


def test_resolve_config_file_prefers_new(tmp_path: Path) -> None:
    new_dir = tmp_path / APP_NAME
    new_dir.mkdir()
    (new_dir / "config.toml").write_text("output_mode = \"plain\"\n", encoding="utf-8")
    legacy_dir = tmp_path / LEGACY_APP_NAME
    legacy_dir.mkdir()
    (legacy_dir / "config.toml").write_text("output_mode = \"tui\"\n", encoding="utf-8")

    assert resolve_config_file(tmp_path) == new_dir / "config.toml"


def test_resolve_config_file_falls_back_to_legacy(tmp_path: Path) -> None:
    legacy_dir = tmp_path / LEGACY_APP_NAME
    legacy_dir.mkdir()
    legacy_file = legacy_dir / "config.toml"
    legacy_file.write_text("output_mode = \"tui\"\n", encoding="utf-8")

    assert resolve_config_file(tmp_path) == legacy_file
