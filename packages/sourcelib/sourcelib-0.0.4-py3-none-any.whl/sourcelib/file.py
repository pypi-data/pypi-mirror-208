from copy import copy
from enum import Enum, auto
from pathlib import Path

from sourcelib.copy import copy as copy_source
from sourcelib.extension import Extension


class ModeMisMatchError(Exception):
    ...


class FileMode(Enum):
    default = auto()


class File:

    EXTENSIONS: dict = {}
    IDENTIFIER: str = "file"

    def __init__(
        self,
        path: Path,
        mode: Enum = FileMode.default,
    ):
        self._mode = mode
        self._path = Path(path).absolute()
        self._original_path = copy(self._path)
        self._extension = self._get_extension(self._path)

    @property
    def mode(self) -> Enum:
        return self._mode

    @property
    def path(self) -> Path:
        return self._path

    @property
    def original_path(self) -> Path:
        return self._path

    @property
    def exists(self) -> bool:
        return self.path.exists()

    def _get_extension(self, path: Path) -> Extension:
        return self.EXTENSIONS[path.suffix]

    def copy(self, destination_folder: Path) -> None:
        if self._extension.folder_coupled is not None:
            copy_source(self._extension.folder_coupled(self._path), destination_folder)
        self._path = copy_source(self._path, destination_folder)

    def __str__(self) -> str:
        return f"Mode: {str(self._mode)} | Path:  {str(self._path)}"

    def __repr__(self):
        return f"File(path={str(self._path)}, mode={str(self._mode)}"