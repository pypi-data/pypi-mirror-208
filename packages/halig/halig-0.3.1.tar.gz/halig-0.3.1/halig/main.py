#!/usr/bin/env python3
from pathlib import Path
from typing import Optional

from rich import print
from typer import Argument, Option, Typer

from halig import literals
from halig.__version__ import __version__
from halig.commands.edit import EditCommand
from halig.commands.notebooks import NotebooksCommand
from halig.commands.show import ShowCommand
from halig.settings import load_from_file
from halig.utils import capture

app = Typer(pretty_exceptions_enable=False, pretty_exceptions_show_locals=False)

config_option = Option(None, "--config", "-c", help=literals.OPTION_CONFIG_HELP)


def complete_note_path(incomplete: str):
    """Build `path = Path(settings.notebooks_root_path / incomplete)`, and complete if:
    - `path` exists:
        - if `path` is a file and ends with `.age`: return it
        - if `path` is a dir: return all its children, non-recursively
    - `path` does not exist: return all occurences of path.glob("*")

    """
    settings = load_from_file()
    path = settings.notebooks_root_path / incomplete
    if path.exists():
        if path.is_dir():
            for child in path.iterdir():
                yield str(child.relative_to(settings.notebooks_root_path))
        elif path.name.endswith(".age"):
            return str(path.relative_to(settings.notebooks_root_path))
    globd = settings.notebooks_root_path.glob(f"{incomplete}*")
    for path in globd:
        yield str(path.relative_to(settings.notebooks_root_path))


@app.command(help=literals.COMMANDS_NOTEBOOKS_HELP)
@capture
def notebooks(
    level: int = Option(  # noqa: B008
        -1,
        "--level",
        "-l",
        help=literals.OPTION_LEVEL_HELP,
    ),
    config: Optional[Path] = config_option,  # noqa: UP007
):
    if level < 0:
        level = float("inf")  # type: ignore[assignment]
    settings = load_from_file(config)
    command = NotebooksCommand(settings=settings, max_depth=level)
    command.run()


@app.command(help=literals.COMMANDS_EDIT_HELP)
@capture
def edit(
    note: Path = Argument(  # noqa: B008
        ...,
        help=literals.ARGUMENT_EDIT_NOTE_HELP,
        autocompletion=complete_note_path,
    ),
    config: Optional[Path] = config_option,  # noqa: UP007
):
    settings = load_from_file(config)
    command = EditCommand(settings=settings, note_path=note)
    command.run()


@app.command(help=literals.COMMANDS_SHOW_HELP)
@capture
def show(
    note: Path = Argument(  # noqa: B008
        ...,
        help=literals.ARGUMENT_SHOW_NOTE_HELP,
        autocompletion=complete_note_path,
    ),
    config: Optional[Path] = config_option,  # noqa: UP007
):
    settings = load_from_file(config)
    command = ShowCommand(settings=settings, note_path=note)
    command.run()


@app.command(help=literals.COMMANDS_VERSION)
@capture
def version():
    print(__version__)


if __name__ == "__main__":
    app()
