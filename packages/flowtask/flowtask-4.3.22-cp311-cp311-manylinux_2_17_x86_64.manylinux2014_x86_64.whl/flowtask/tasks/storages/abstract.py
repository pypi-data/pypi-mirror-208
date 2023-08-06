from typing import Any
from pathlib import PurePath
from abc import ABC, abstractmethod
from navconfig.logging import logging


class AbstractTaskStorage(ABC):

    def __init__(self, *args, **kwargs) -> None:
        self._program: str = None
        self.path: PurePath = None
        self.taskpath: PurePath = None
        self.logger = logging.getLogger('FlowTask.Task.Storage')

    def set_program(self, program:str) -> None:
        self._program = program

    @abstractmethod
    async def open_task(
        self,
        taskname: str,
    ) -> Any:
        """open_task.
            Open A Task from Task Storage, support json, yaml and toml formats.
        """
