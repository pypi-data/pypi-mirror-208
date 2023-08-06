from typing import Union
from pathlib import Path, PurePath
from flowtask.exceptions import (
    FlowTaskError,
    TaskNotFound,
    TaskParseError,
    TaskDefinition
)
from flowtask.parsers import (
    JSONParser,
    TOMLParser,
    YAMLParser
)
from .abstract import AbstractTaskStorage


class FileTaskStorage(AbstractTaskStorage):
    """Saving Tasks on Filesystem.
    """
    def __init__(self, path: PurePath, *args, **kwargs):
        super(FileTaskStorage, self).__init__(*args, **kwargs)
        if not path:
            ## Default Task Path
            raise FlowTaskError(
                "Required Task Path for Filesystem Task Storage"
            )
        else:
            self.path = path
            if isinstance(path, str):
                self.path = Path(path)

    def set_program(self, program: str) -> None:
        if not program:
            program = 'default'
        self._program = program
        self.taskpath = self.path.joinpath(self._program, 'tasks')
        self.logger.notice(f'Program Task Path: {self.taskpath}')

    async def open_task(
        self,
        taskname: str,
    ) -> Union[dict, str]:
        """open_task.
            Open A Task from FileSystem, support json, yaml and toml formats.
        """
        for f in ('json', 'yaml', 'toml', ):
            filename = self.taskpath.joinpath(f'{taskname}.{f}')
            if filename.exists():
                self.logger.debug(f'Task File: {filename}')
                try:
                    if f == 'json':
                        parse = JSONParser(str(filename))
                    elif f == 'yaml':
                        parse = YAMLParser(str(filename))
                    elif f == 'toml':
                        parse = TOMLParser(str(filename))
                    return await parse.run()
                except TaskParseError as err:
                    raise TaskParseError(
                        f"Task Parse Error: {err}"
                    ) from err
                except Exception as err:
                    raise TaskDefinition(
                        f'DI: Error Parsing {f} Task in {taskname}: {err}'
                    ) from err
        raise TaskNotFound(
            f'DI: Task {taskname} Not Found'
        )
