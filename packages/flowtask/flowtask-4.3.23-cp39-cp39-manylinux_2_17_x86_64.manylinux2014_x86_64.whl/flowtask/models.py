"""Task Models.

Models for Tasks/Jobs structure.
"""
import asyncio
from typing import Dict
from datetime import datetime
import uuid
import enum
import logging
from navconfig.conf import asyncpg_url
from asyncdb.models import Model, Column
from asyncdb import AsyncDB
from asyncdb.exceptions import NoDataFound


class TaskState(enum.Enum):
    IDLE = 0, 'Idle'
    PENDING = 1, 'Pending'
    STARTED = 2, 'Started'
    RUNNING = 3, 'Task Running'
    STOPPED = 4, 'Task Stopped'
    DONE = 5, 'Done'
    DONE_WITH_NODATA = 6, 'Done (No Data)'
    NOT_FOUND = 7, 'Not Found'
    FAILED = 9, 'Task Failed'
    DONE_WITH_WARNINGS = 10, 'Warning'
    SKIPPED = 11, 'Skipped'
    ERROR = 12, 'Task Error'
    EXCEPTION = 98, 'Task Exception'
    CLOSED = 99, 'Closed'

    def __new__(cls, value, name):
        member = object.__new__(cls)
        member._value_ = value
        member.label = name
        return member

    def __int__(self):
        return self.value


def at_now():
    return datetime.now()


class TaskModel(Model):
    task: str = Column(required=True, primary_key=True)
    task_id: uuid.UUID = Column(required=False)
    task_function: str = Column(required=False)
    task_path: str = Column(required=False)
    task_definition: Dict = Column(required=False, db_type='jsonb')
    url: str = Column(required=False)
    url_response: str = Column(required=False, default='json')
    attributes: Dict = Column(required=False, db_type='jsonb')
    params: Dict = Column(required=False, db_type='jsonb')
    enabled: bool = Column(required=False, default=True)
    is_coroutine: bool = Column(required=False, default=False)
    executor: str = Column(required=False, default='default')
    last_started_time: datetime = Column(required=False)
    last_exec_time: datetime = Column(required=False)
    last_done_time: datetime = Column(required=False)
    created_at: datetime = Column(
        required=False,
        default=at_now(),
        db_default='now()'
    )
    updated_at: datetime = Column(
        required=False,
        default=at_now(),
        db_default='now()'
    )
    program_id: int = Column(required=False, default=1)
    program_slug: str = Column(required=False, default='navigator')
    is_queued: bool = Column(required=False, default=False)
    task_state: TaskState = Column(required=False, default=TaskState.IDLE)
    traceback: str = Column(required=False)
    file_id: int = Column(required=False)
    storage: str = Column(required=False, default='default', comment='Task Storage')

    class Meta:
        driver = 'pg'
        name = 'tasks'
        schema = 'troc'
        app_label = 'troc'
        strict = True
        frozen = False
        remove_nulls = True # Auto-remove nullable (with null value) fields

async def setTaskState(task, message, event_loop, **kwargs):
    """
    Set the task state on Task Table:
    """
    exec_time = datetime.now()
    asyncio.set_event_loop(event_loop)
    state = task.getState()
    taskinfo = {
        "program_slug": task.getProgram(),
        "task": task.taskname
    }
    data = {
        'task_state': int(state)
    }
    if state == TaskState.STARTED:
        data['last_started_time'] = exec_time
        data['traceback'] = None
    elif state == TaskState.STOPPED:
        data['last_exec_time'] = exec_time
        data['traceback'] = f"{message!s}"
    elif state in (TaskState.FAILED, TaskState.ERROR, TaskState.EXCEPTION):
        data['last_exec_time'] = exec_time
        if 'cls' in kwargs:
            e = str(kwargs['cls']).replace("'", "")
            data['traceback'] = f"{e!s}"
        elif 'trace' in kwargs:
            data['traceback'] = f"{kwargs['trace']!s}"
        elif 'error' in kwargs:
            data['traceback'] = f"{kwargs['error']!s}"
        else:
            data['traceback'] = f"{message!s}"
    elif state in (TaskState.DONE, TaskState.DONE_WITH_NODATA, TaskState.DONE_WITH_WARNINGS):
        if 'cls' in kwargs:
            data['traceback'] = f"{kwargs['cls']!s}"
        elif 'error' in kwargs:
            data['traceback'] = f"{kwargs['error']!s}"
        else:
            data['traceback'] = f"{message!s}"
        data['last_exec_time'] = exec_time
        data['last_done_time'] = exec_time
    if schema := task.schema():
        # is a database-based task
        db = AsyncDB("pg", dsn=asyncpg_url, loop=event_loop)
        try:
            async with await db.connection() as conn: # pylint: disable=E1101
                TaskModel.Meta.schema = schema
                TaskModel.Meta.connection = conn
                # print('TASK ', taskinfo, data)
                try:
                    task = await TaskModel.get(**taskinfo)
                    for key, val in data.items():
                        setattr(task, key, val)
                    result = await task.update()
                    # we can return the related task to used someone else
                    return result
                except NoDataFound as err:
                    logging.error(err)
                    # task doesn't exists
                    return None
        except Exception as err:
            logging.error(err)
            raise Exception(err) from err
    else:
        # sending "data" to logging info
        data = {**taskinfo, **data}
        logging.info(data)
        return data
