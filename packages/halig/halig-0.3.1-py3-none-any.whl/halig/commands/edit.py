import os
import subprocess
import tempfile
from pathlib import Path

from halig import utils
from halig.commands.base import BaseCommand
from halig.encryption import Encryptor
from halig.settings import Settings


class EditCommand(BaseCommand):
    """*The* edit command, which also encompasses creating a new file when needed,
    that is, when `note_path` is a folder, a new YYYY-MM-DD.age file will be created
    if it does not exist and filled with an encrypted empty string

    Attributes:
       note_path (Path): The path to a specific .age note or a notebook.
           Note that the input note_path will be modified in order to append it
           to the notebooks root path defined by `Settings.notebooks_root_path`
           attribute. This means that the input path is relative to the mentioned
           root path
       settings (Settings): Settings object
       encryptor (Encryptor): Encryptor object
    """

    def __init__(self, note_path: Path, settings: Settings):
        super().__init__(settings)

        self.note_path = self.settings.notebooks_root_path / note_path
        self.encryptor = Encryptor(self.settings)

        if self.note_path.is_dir():
            self.note_path /= f"{utils.now().date()}.age"

        if not self.note_path.name.endswith(".age"):
            err = f"File {self.note_path.name} is not a valid AGE file"
            raise ValueError(err)

        if not self.note_path.exists():
            empty_encrypted = self.encryptor.encrypt("")
            with self.note_path.open("wb") as f:
                f.write(empty_encrypted)

    def edit_contents(self, original_contents: bytes) -> bytes:
        """Let the user edit the contents by opening an in-memory tempfile
        using $EDITOR and encrypt the new contents

        Args:
            original_contents (bytes): original data that will be dumped into the
                tempfile for the user to modify
        Returns:
            modified data as bytes
        """

        with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as tf:
            tf.write(original_contents)
            temp_path = Path(tf.name)

        editor = os.environ.get("EDITOR", "vim")
        subprocess.call([editor, temp_path])  # noqa: S603

        with temp_path.open("rb") as f:
            new_contents = f.read()
        encrypted_contents = self.encryptor.encrypt(new_contents)

        temp_path.unlink()
        return encrypted_contents

    def run(self):
        with self.note_path.open("rb") as f:
            original_contents = f.read()
        original_contents = self.encryptor.decrypt(original_contents)
        new_contents = self.edit_contents(original_contents)
        with self.note_path.open("wb") as f:
            f.write(new_contents)
