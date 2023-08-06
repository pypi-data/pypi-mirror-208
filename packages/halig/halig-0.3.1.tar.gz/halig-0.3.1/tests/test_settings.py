from pathlib import Path

import pytest

from halig.settings import Settings, load_from_file


def test_settings_from_env(settings: Settings, notebooks_root_path_envvar):
    from_env_settings = Settings()  # type: ignore[call-arg]
    assert from_env_settings.notebooks_root_path == settings.notebooks_root_path


def test_settings_from_non_existing_file_raises_value_error():
    with pytest.raises(ValueError, match="field required"):
        Settings()  # type: ignore[call-arg]


def test_load_from_file(notebooks_path: Path, settings_file_path: Path):
    settings = load_from_file(settings_file_path)
    assert settings.notebooks_root_path == notebooks_path


def test_load_from_existing_standard_file(settings_file_path: Path, settings: Settings):
    standard_settings = load_from_file()
    assert standard_settings.notebooks_root_path == settings.notebooks_root_path


def test_load_from_empty_file_raises_value_error(empty_file_path: Path):
    with pytest.raises(ValueError, match=f"File {empty_file_path} is empty"):
        load_from_file(empty_file_path)


def test_load_from_non_existing_file_path_raises_file_not_found_error(halig_path: Path):
    file = halig_path / "some_invalid_file.yml"
    with pytest.raises(FileNotFoundError, match=f"File {file} does not exist"):
        load_from_file(file)
