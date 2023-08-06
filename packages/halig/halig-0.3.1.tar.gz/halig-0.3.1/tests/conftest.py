import json
import os
from pathlib import Path

import pytest
import yaml
from pyrage.ssh import Identity, Recipient

from halig.encryption import Encryptor
from halig.settings import Settings


@pytest.fixture()
def halig_ssh_public_key():
    return (
        "ssh-ed25519 "
        "AAAAC3NzaC1lZDI1NTE5AAAAIGjHhIF/DlVCb2dRFMlKia7nij1Aq+zRDCaMIwe/VKDh"
        " foo@bar"
    )


@pytest.fixture()
def halig_ssh_private_key():
    return """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACBox4SBfw5VQm9nURTJSomu54o9QKvs0QwmjCMHv1Sg4QAAAJhvD2Jxbw9i
cQAAAAtzc2gtZWQyNTUxOQAAACBox4SBfw5VQm9nURTJSomu54o9QKvs0QwmjCMHv1Sg4Q
AAAEAZANW15ieou1ds73BlM1nqzyZ2A0454JnB3QirZycGv2jHhIF/DlVCb2dRFMlKia7n
ij1Aq+zRDCaMIwe/VKDhAAAAEXJvb3RANGNjNWUxOWYyYThiAQIDBA==
-----END OPENSSH PRIVATE KEY-----
"""


@pytest.fixture()
def ssh_identity(halig_ssh_private_key: str) -> Identity:
    return Identity.from_buffer(halig_ssh_private_key.encode())


@pytest.fixture()
def ssh_recipient(halig_ssh_public_key: str) -> Recipient:
    return Recipient.from_str(halig_ssh_public_key)


@pytest.fixture()
def halig_path(fs, halig_ssh_public_key, halig_ssh_private_key) -> Path:
    fs.add_real_paths(["/etc/localtime"])
    ssh_path = Path("~/.ssh").expanduser()
    ssh_path.mkdir(parents=True)

    with (ssh_path / "id_ed25519").open("w") as f:
        f.write(halig_ssh_private_key)

    with (ssh_path / "id_ed25519.pub").open("w") as f:
        f.write(halig_ssh_public_key)

    halig_path = Path("~/.config/halig").expanduser()
    halig_path.mkdir(parents=True)
    return halig_path


@pytest.fixture()
def notebooks_path(halig_path) -> Path:
    notebooks_path = Path("~/Notebooks").expanduser()
    notebooks_path.mkdir(parents=True)
    return notebooks_path


@pytest.fixture()
def settings(notebooks_path: Path) -> Settings:
    return Settings(notebooks_root_path=notebooks_path)


@pytest.fixture()
def settings_file_path(halig_path: Path, notebooks_path: Path) -> Path:
    yaml_file = halig_path / "halig.yml"
    yaml_file.touch()
    s = Settings(notebooks_root_path=notebooks_path)
    # `.dict()` doesn't serialize some fields that yaml doesn't understand
    serialized = json.loads(s.json())
    with yaml_file.open("w") as f:
        yaml.safe_dump(serialized, f)
    return yaml_file


@pytest.fixture()
def empty_file_path(halig_path: Path) -> Path:
    empty_path = halig_path / "empty"
    empty_path.touch()
    return empty_path


@pytest.fixture()
def notebooks_root_path_envvar(notebooks_path: Path):
    os.environ["HALIG_NOTEBOOKS_ROOT_PATH"] = str(notebooks_path)
    yield notebooks_path
    del os.environ["HALIG_NOTEBOOKS_ROOT_PATH"]


@pytest.fixture()
def encryptor(settings: Settings) -> Encryptor:
    return Encryptor(settings)
