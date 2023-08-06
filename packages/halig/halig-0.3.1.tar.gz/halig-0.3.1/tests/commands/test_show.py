from pathlib import Path

import pytest

from halig.commands.show import ShowCommand
from halig.settings import Settings


def test_show_raises_note_path_does_not_exist(notes, settings: Settings):
    with pytest.raises(ValueError, match="does not exist"):
        ShowCommand(
            Path("foo"),
            settings=settings,
        )


def test_show_raises_note_path_is_not_age_valid(notes, settings: Settings):
    note_path = settings.notebooks_root_path / "foo.txt"
    note_path.touch()
    with pytest.raises(ValueError, match="is not a valid AGE file"):
        ShowCommand(
            note_path,
            settings=settings,
        )


def test_show_current_note(current_note, settings):
    show_command = ShowCommand(
        note_path=settings.notebooks_root_path, settings=settings
    )
    assert show_command.note_path == current_note
    assert show_command.decrypt() == "foo"


def test_show_current_daily(current_daily, settings: Settings):
    show_command = ShowCommand(note_path=current_daily, settings=settings)
    assert show_command.note_path == current_daily
    assert show_command.decrypt() == "foo"
