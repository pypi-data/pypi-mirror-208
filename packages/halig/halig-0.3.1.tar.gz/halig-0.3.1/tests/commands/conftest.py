from pathlib import Path

import pendulum
import pytest as pytest

from halig import utils
from halig.commands.notebooks import NotebooksCommand
from halig.settings import Settings


@pytest.fixture()
def notes(notebooks_path: Path):
    personal = notebooks_path / "Personal"
    work = notebooks_path / "Work"
    personal.mkdir()
    work.mkdir()

    personal_todos = personal / "todos.age"
    personal_todos.touch()

    work_todos = work / "todos.age"
    work_todos.touch()

    dailies = work / "Dailies"
    dailies.mkdir()

    dt = pendulum.now()
    for day_offset in range(10):
        dt = dt.subtract(days=day_offset)
        (dailies / f"{dt.date()}.age").touch()


@pytest.fixture
def notebooks_command(settings: Settings):
    return NotebooksCommand(max_depth=float("inf"), settings=settings)


@pytest.fixture()
def current_note(notes, settings, encryptor) -> Path:
    note_path = settings.notebooks_root_path / f"{utils.now().date()}.age"
    note_path.touch()
    data = encryptor.encrypt("foo".encode())
    with note_path.open("wb") as f:
        f.write(data)
    return note_path


@pytest.fixture
def current_daily(notes, settings, encryptor) -> Path:
    note_path = (
        settings.notebooks_root_path / "Work" / "Dailies" / f"{utils.now().date()}.age"
    )
    data = encryptor.encrypt("foo".encode())
    with note_path.open("wb") as f:
        f.write(data)
    return note_path


@pytest.fixture
def mock_edit(mocker):
    def edit(callargs: list):
        with open(callargs[1], "wb") as f:
            f.write("edited".encode())

    mocker.patch("halig.commands.edit.subprocess.call", side_effect=edit)
