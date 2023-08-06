from typing import Any, Union
from abc import ABC, abstractmethod
from navconfig import DEBUG
from navconfig.logging import logging


class AbstractStore(ABC):
    """Abstract class for File Store.
    """

    def __init__(self, *args, **kwargs) -> None:
        self._program: Any = None
        self.logger = logging.getLogger('FlowTask.Files.Store')
        if DEBUG is True:
            self.logger.notice(f'Starting Store {self.__class__.__name__}')
        self.kwargs = kwargs

    def set_program(self, program:str) -> None:
        self._program = program
