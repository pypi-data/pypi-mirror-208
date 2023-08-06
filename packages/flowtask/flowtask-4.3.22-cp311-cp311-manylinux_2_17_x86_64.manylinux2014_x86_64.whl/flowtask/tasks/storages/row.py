from typing import Any
from flowtask.exceptions import TaskError
from .abstract import AbstractTaskStorage


class RowTaskStorage(AbstractTaskStorage):
    """Task is saved directly into Task Table (SQL).
    """

    def __init__(self, column_name: str = 'task_definition', *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._column = column_name

    def set_definition(self, obj) -> None:
        try:
            self._task = obj[self._column]
        except (KeyError, AttributeError) as exc:
            raise TaskError(
                f"Unable to load Task definition from Table: {exc}"
            ) from exc

    async def open_task(
        self,
        taskname: str,
    ) -> Any:
        return self._task
