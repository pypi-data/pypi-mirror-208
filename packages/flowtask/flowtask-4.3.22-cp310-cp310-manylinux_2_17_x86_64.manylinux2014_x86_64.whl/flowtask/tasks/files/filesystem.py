from typing import Union
from pathlib import Path, PurePath
from .abstract import AbstractStore


class FileStore(AbstractStore):
    def __init__(self, path: Union[str, PurePath], *args, **kwargs) -> None:
        if isinstance(path, str):
            path = Path(path)
        self.path: PurePath = path
        super().__init__(*args, **kwargs)
