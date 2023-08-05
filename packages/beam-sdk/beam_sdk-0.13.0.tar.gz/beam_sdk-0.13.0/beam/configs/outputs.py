from typing import List

from beam.base import AbstractDataLoader
from beam.serializer import FileConfiguration
from beam.types import OutputType


class OutputManager(AbstractDataLoader):
    def __init__(self) -> None:
        self.files: List[FileConfiguration] = []
        self.dirs: List[FileConfiguration] = []

    def File(self, path: str, name: str, **_):
        self.files.append(
            FileConfiguration(path=path, name=name, output_type=OutputType.File)
        )

    def Dir(self, path: str, name: str, **_):
        self.dirs.append(
            FileConfiguration(path=path, name=name, output_type=OutputType.Directory)
        )

    def dumps(self):
        return [
            *[f.validate_and_dump() for f in self.files],
            *[d.validate_and_dump() for d in self.dirs],
        ]

    def from_config(self, outputs: List[dict]):
        if outputs is None:
            return

        for f in outputs:
            if f.get("output_type") == OutputType.Directory:
                self.Dir(**f)
            else:
                self.File(**f)
