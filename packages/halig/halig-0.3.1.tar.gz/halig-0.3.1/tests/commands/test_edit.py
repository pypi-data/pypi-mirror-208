import pytest

from halig.commands.edit import EditCommand
from halig.settings import Settings


def test_edit_raises_invalid_age_file(notes, settings: Settings):
    note_path = settings.notebooks_root_path / "foo.txt"
    note_path.touch()
    with pytest.raises(ValueError, match="is not a valid AGE file"):
        EditCommand(
            note_path,
            settings=settings,
        )


def test_edit_current_note(mock_edit, current_note, settings: Settings, encryptor):
    edit_command = EditCommand(
        note_path=settings.notebooks_root_path, settings=settings
    )
    assert edit_command.note_path == current_note
    edit_command.run()
    with current_note.open("rb") as f:
        contents = encryptor.decrypt(f.read()).decode()
    assert contents == "edited"


def test_edit_current_daily(mock_edit, current_daily, settings, encryptor):
    current_daily.unlink()
    edit_command = EditCommand(note_path=current_daily, settings=settings)
    assert edit_command.note_path == current_daily
    edit_command.run()
    with current_daily.open("rb") as f:
        contents = encryptor.decrypt(f.read()).decode()
    assert contents == "edited"
