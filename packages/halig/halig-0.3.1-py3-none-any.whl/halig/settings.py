from functools import lru_cache
from pathlib import Path
from typing import Any

import httpx
import httpx_cache
import platformdirs
import yaml
from pydantic import BaseSettings, DirectoryPath, FilePath, HttpUrl, validator


class Settings(BaseSettings):
    """Settings model. It mainly stores paths that are interesting to the project.
     All the path-attributes described below have a validity check upon instantiation,
     meaning that they should exist and be readable and/or writable

    Attributes:
        notebooks_root_path (DirectoryPath): a *valid* path to a directory that
            may contain notes or other notebooks
        identity_paths (list[FilePath]): a list of *valid* paths of private keys.
            Defaults to `[~/.ssh/id_ed25519]`
        recipient_paths (list[FilePath|HttpUrl]): a list *valid* paths of public keys,
            which usually is understood as a public key. Defaults to
            `[~/.ssh/id_ed25519.pub]`
    """

    notebooks_root_path: DirectoryPath
    identity_paths: list[FilePath] = [Path("~/.ssh/id_ed25519").expanduser()]
    recipient_paths: list[FilePath | HttpUrl] = [
        Path("~/.ssh/id_ed25519.pub").expanduser(),
    ]

    @validator("identity_paths", "recipient_paths", pre=True)
    def validate_paths(cls, v: Any):  # noqa: N805
        if not isinstance(v, list):
            v = [v]
        new_v = []
        for path in v:
            new_path = path
            if isinstance(path, str) and not path.startswith("http"):
                new_path = Path(path)
            new_v.append(
                new_path.expanduser() if isinstance(new_path, Path) else new_path,
            )
        return new_v

    @validator("notebooks_root_path", pre=True)
    def validate_notebooks_path(cls, v: Any):  # noqa: N805
        if isinstance(v, str):
            return Path(v).expanduser()
        if isinstance(v, Path):
            return v.expanduser()
        return v

    def load_private_keys(self) -> set[str]:
        keys = set()
        for path in self.identity_paths:
            with path.open("r") as f:
                keys.add(f.read())
        return keys

    def load_public_keys(self) -> set[str]:
        keys = set()
        for path in self.recipient_paths:
            if isinstance(path, HttpUrl):
                with httpx_cache.Client(cache=httpx_cache.FileCache()) as client:
                    response = client.get(str(path))
                if response.status_code == httpx.codes.OK:
                    for line in response.content.decode().split("\n"):
                        if line:
                            keys.add(line)
            elif isinstance(path, Path):
                with path.open("r") as f:
                    keys.add(f.read())
        return keys

    class Config:
        env_prefix = "halig_"


@lru_cache
def load_from_file(file_path: Path | None = None) -> Settings:
    if file_path is None:
        halig_config_home = Path(
            platformdirs.user_config_dir("halig", ensure_exists=True),
        )
        file_path = halig_config_home / "halig.yml"
        file_path.touch(exist_ok=True)
    elif not file_path.exists():
        err = f"File {file_path} does not exist"
        raise FileNotFoundError(err)

    with file_path.open("r") as f:
        data = yaml.safe_load(f)
    if not data:
        err = f"File {file_path} is empty"
        raise ValueError(err)
    return Settings(**data)
