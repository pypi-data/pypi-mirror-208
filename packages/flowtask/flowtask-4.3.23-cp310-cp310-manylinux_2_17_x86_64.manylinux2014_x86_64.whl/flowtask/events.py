# -*- coding: utf-8 -*-
"""Data-Integration Task Events.

Event System for DataIntegration tasks.
"""
import asyncio
import traceback
from datetime import datetime
import socket
from typing import List, Any
from collections.abc import Callable, Awaitable
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from asyncdb import AsyncDB
from asyncdb.exceptions import (
    default_exception_handler
)
# logging system
from navconfig.logging import logging
## Notify System
from notify import Notify
from notify.providers.email import Email
from notify.providers.slack import Slack
from notify.models import Actor, Chat, Channel
from flowtask.conf import (
    DEBUG,
    SEND_NOTIFICATIONS,
    EVENT_CHAT_ID,
    EVENT_CHAT_BOT,
    NOTIFY_ON_ERROR,
    NOTIFY_ON_SUCCESS,
    NOTIFY_ON_FAILURE,
    NOTIFY_ON_WARNING,
    DEFAULT_RECIPIENT,
    EMAIL_USERNAME,
    EMAIL_PASSWORD,
    EMAIL_PORT,
    EMAIL_HOST,
    ENVIRONMENT,
    TASK_EXEC_BACKEND,
    TASK_EXEC_CREDENTIALS,
    TASK_EVENT_TABLE,
    INFLUX_DATABASE,
    INFLUX_TASKS_STARTED,
    USE_TASK_EVENT,
    SLACK_DEFAULT_CHANNEL,
    SLACK_DEFAULT_CHANNEL_NAME
)
from flowtask.utils.functions import check_empty
from flowtask.utils.json import json_encoder


EVENT_HOST = socket.gethostbyname(socket.gethostname())

class TaskEvent(object):
    """
    Basic Event Manager of flowtask.
    """

    def __init__(self):
        self._handlers: List[Callable] = []

    class Event:
        def __init__(self, func: List[Callable]) -> None:
            if not isinstance(func, list):
                raise TypeError('Function parameter need to be a List')
            self._handlers = func

        def __iadd__(self, func):
            self._handlers.append(func)
            return self

        def __isub__(self, func):
            self._handlers.remove(func)
            return self

        def __call__(self, *args, **kwargs):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # creating the executor
            fn = partial(executeEvent, handlers=self._handlers,
                         *args, **kwargs)
            # sending function coroutine to a thread
            with ThreadPoolExecutor(max_workers=10) as pool:
                loop.run_in_executor(pool, fn)

    @classmethod
    def addEvent(cls, **kwargs):
        """
        addEvent( event1 = [f1,f2,...], event2 = [g1,g2,...], ... )
        creates events using **kwargs to create any number of events.
        Each event recieves a list of functions,
        where every function in the list recieves the same parameters.
        Example:
        def hello(): print "Hello ",
        def world(): print "World"

        TaskEvent.addEvent( salute = [hello] )
        TaskEvent.salute += world

        TaskEvent.salute()

        Output:
        Hello World
        """
        for key, value in kwargs.items():
            if not isinstance(value, list):
                raise ValueError(
                    "Parameter for function Name must be a List"
                )
            else:
                kwargs[key] = cls.Event(value)
            setattr(cls, key, kwargs[key])


def executeEvent(
        handlers: List[Awaitable],
        *args,
        **kwargs
):
    """
    executeEvent.

    Executing coroutine Functions associated with an event into a Event Loop.
    """
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.set_exception_handler(default_exception_handler)
    tasks = []
    for fn in handlers:
        if asyncio.iscoroutinefunction(fn):
            try:
                task = event_loop.create_task(
                    fn(event_loop=event_loop, *args, **kwargs)
                )
            except Exception as e:
                logging.exception(e, stack_info=True)
            tasks.append(task)
            results = event_loop.run_until_complete(
                asyncio.gather(*tasks, return_exceptions=True)
            )
            for task in results:
                if isinstance(task, Exception):
                    logging.exception(task)
        else:
            try:
                state = fn(*args, **kwargs)
            except Exception as err:
                print('ERR ', err)
                logging.exception(err)
                raise Exception(err)


# Event utiliy functions
def logEvent(
    message: str = '',
    task: Callable = None,
    result: Any = None,
    cls: Exception = None,
    **kwargs
):
    msg = message
    if not msg:
        msg = getattr(cls, 'message', str(cls))
    if DEBUG:
        logging.debug(msg)
    else:
        logging.info(msg)


def getNotify(notify, **kwargs):
    if notify == 'telegram':
        # defining the Default chat object:
        recipient = Chat(**{"chat_id": EVENT_CHAT_ID, "name": "Navigator"})
        # send notifications to Telegram bot
        args = {
            "bot_token": EVENT_CHAT_BOT,
            **kwargs
        }
        ntf = Notify('telegram', **args)
    elif notify == 'slack':
        recipient = Channel(
            channel_id=SLACK_DEFAULT_CHANNEL,
            channel_name=SLACK_DEFAULT_CHANNEL_NAME
        )
        ntf = Slack()
    elif notify == 'email':
        account = {
            "host": EMAIL_HOST,
            "port": EMAIL_PORT,
            "username": EMAIL_USERNAME,
            "password": EMAIL_PASSWORD,
            **kwargs
        }
        recipient = Actor(**DEFAULT_RECIPIENT)
        ntf = Email(debug=True, **account)
    else:
        recipient = Actor(**DEFAULT_RECIPIENT)
        ntf = Notify(notify, **kwargs)
    return [ntf, recipient]


async def notifyOnSuccess(
    message: str = '',
    result: Any = None,
    event_loop: asyncio.AbstractEventLoop = None,
    **kwargs
):
    """
    notifyOnSuccess.

    Processing event when a task finished correctly
    """
    ntf, recipients = getNotify(NOTIFY_ON_SUCCESS)
    if not check_empty(result):
        message = f'✅ ::{ENVIRONMENT} -  {message!s}'
    else:
        message = f'⚠️ ::{ENVIRONMENT} -  {message!s}, Empty Result.'
    # start sending notifications
    if SEND_NOTIFICATIONS is True:
        args = {
            "recipient": [recipients],
            "message": message,
            **kwargs
        }
        if ntf.provider_type == 'email':
            args['subject'] = message
        elif ntf.provider == 'telegram':
            args["disable_notification"] = True
        else:
            args['subject'] = message
        result = await ntf.send(**args)
    return result


async def notifyEvent(
    message: str = '',
    result: Any = None,
    error: str = None,
    cls: Callable = None,
    trace: str = None,
    task: Callable = None,
    event_loop: asyncio.AbstractEventLoop = None,
    **kwargs
):
    """
    notifyEvent.

    Processing events and send notification to users.
    """
    program = task.getProgram()
    task = task.taskname

    if message is not None and result is not None:
        # success event:
        ntf, recipients = getNotify(NOTIFY_ON_SUCCESS)
        message = f'✅ ::{ENVIRONMENT} -  {message!s}'
    elif trace is not None:
        ntf, recipients = getNotify(NOTIFY_ON_FAILURE)
        message = f'🛑 ::{ENVIRONMENT} -  {error!s}'
    elif message == '':
        program = None
        task = None
        component = None
        if not error:
            error = str(cls)
        if 'component' in kwargs:
            component = kwargs['component']
            del kwargs['component']
        if program and task and component:
            message = f'🛑 ::{ENVIRONMENT} -  Task {program}.{task}, Error on {component}: {error!s}'
        elif program and task:
            message = f'🛑 ::{ENVIRONMENT} -  Error on {program}.{task}: {error!s}'
        elif task:
            message = f'🛑 ::{ENVIRONMENT} -  Error on {task}, raised {cls.__class__!s}: {error!s}'
        else:
            message = f'⚠️ ::{ENVIRONMENT} -  Task Error: {error!s}'
        ntf, recipients = getNotify(NOTIFY_ON_ERROR, **kwargs)
    else:
        # is a warning
        ntf, recipients = getNotify(NOTIFY_ON_WARNING, **kwargs)
        msg = result if result is not None else message
        message = f'⚠️ ::{ENVIRONMENT} -  {msg!s}'
    # start sending notifications
    if SEND_NOTIFICATIONS is True:
        args = {
            "recipient": [recipients],
            "message": message,
        }
        if ntf.provider_type == 'email':
            args['subject'] = message
        if ntf.provider == 'telegram':
            args["disable_notification"] = True
        print('ARGS: ', args)
        result = await ntf.send(**args)
        return result


async def notifyFailure(
    error: str = '',
    cls: Callable = None,
    task: Callable = None,
    event_loop: asyncio.AbstractEventLoop = None,
    **kwargs
):
    """
    notifyFailure.

    Processing events and send notification to users.
    """
    trace = ''
    if 'stacktrace' in kwargs:
        trace = kwargs['stacktrace']
    program = task.getProgram()
    task = task.taskname
    if cls is not None:
        if hasattr(cls, 'message'):
            msg = cls.message
        else:
            msg = str(cls)
    else:
        msg = error
    if program and task:
        message = f'🛑 ::{ENVIRONMENT} -  Task {program}.{task}, {msg!s}'
    else:
        message = f'🛑 ::{ENVIRONMENT} -  {msg!s}'
    if trace:
        message = message + f'\n `*{trace}*`'
    ntf, recipients = getNotify(NOTIFY_ON_FAILURE, **kwargs)
    if SEND_NOTIFICATIONS is True:
        # send first notification to telegram
        # result = await telegram.send(
        #     recipient=chat,
        #     message=message,
        #     disable_notification=True
        # )
        # and the other component:
        args = {
            "recipient": [recipients],
            "message": message,
        }
        result = await ntf.send(**args)
        return result


async def notifyWarning(
    cls: Callable = None,
    task: Callable = None,
    event_loop: asyncio.AbstractEventLoop = None,
    **kwargs
):
    """
    notifyWarning.

    Processing events and send notification to users.
    """
    program = task.getProgram()
    task = task.taskname
    component = None
    status = None
    if 'status' in kwargs:
        status = kwargs['status']
        del kwargs['status']
    if 'component' in kwargs:
        component = kwargs['component']
        del kwargs['component']
    if 'message' in kwargs:
        msg = kwargs['message']
        del kwargs['message']
    else:
        msg = None
    if program and task and component:
        message = f'⚠️ ::{ENVIRONMENT} - *{program}.{task}*: Warning {component}->{str(msg)!s}: {status}'
    elif program and task:
        message = f'⚠️ ::{ENVIRONMENT} - *{program}.{task}*: {str(msg)!s}: {status}'
    else:
        message = f'⚠️ ::{ENVIRONMENT} - {str(msg)!s}: {status}'
    # telegram, chat = getNotify('telegram')
    ntf, recipients = getNotify(NOTIFY_ON_WARNING, **kwargs)
    result = None
    if SEND_NOTIFICATIONS is True:
        args = {
            "recipient": [recipients],
            "message": message,
        }
        if ntf.provider_type == 'email':
            args['subject'] = message
        if ntf.provider == 'telegram':
            args["disable_notification"] = True
        async with ntf as conn:
            result = await conn.send(**args)
    return result


async def saveExecution(
    cls: Callable = None,
    task: Callable = None,
    result: Any = None,
    event_loop: asyncio.AbstractEventLoop = None,
    **kwargs
) -> None:
    # saving the log into a database.
    msg = None
    if 'message' in kwargs:
        msg = kwargs['message']
    elif cls is not None:
        msg = getattr(cls, 'message', str(cls))
    if 'status' not in kwargs:
        status = 'done'
    else:
        status = kwargs['status']
    db = AsyncDB(
            TASK_EXEC_BACKEND,
            params=TASK_EXEC_CREDENTIALS,
            loop=event_loop
    )
    stat = task.stats # getting the stat object:
    if stat:
        stats = json_encoder(stat.to_json())
        start_time = stat.start_time
        end_time = stat.finish_time
        duration = stat.duration
    else:
        stats = {}
        start_time = None
        end_time = datetime.utcnow()
        duration = None
    if USE_TASK_EVENT is True:
        async with await db.connection() as conn:
            try:
                data = {
                    "measurement": TASK_EVENT_TABLE,
                    "location": ENVIRONMENT,
                    "timestamp": end_time,
                    "fields": {
                        "status": status
                    },
                    "tags": {
                        "host": EVENT_HOST,
                        "region": ENVIRONMENT,
                        "stats": stats,
                        "start_time": start_time,
                        "finish_time": end_time,
                        "duration": duration,
                        "tenant": task.getProgram(),
                        "task": task.taskname,
                        "id": task.task_id,
                        "traceback": traceback.format_exc(),
                        "message": msg
                    }
                }
                await conn.write(data, bucket=INFLUX_DATABASE)
            except Exception as e:
                logging.error(
                    f'DI: Error saving Task Execution: {e}'
                )
                print(traceback.format_exc())


async def startedTask(
    cls: Callable = None,
    task: Callable = None,
    result: Any = None,
    event_loop: asyncio.AbstractEventLoop = None,
    **kwargs
) -> None:
    # saving the log into a database.
    influx = AsyncDB(
            TASK_EXEC_BACKEND,
            params=TASK_EXEC_CREDENTIALS,
            loop=event_loop
    )
    start_time = datetime.utcnow()
    if USE_TASK_EVENT is True:
        async with await influx.connection() as conn:
            try:
                data = {
                    "measurement": INFLUX_TASKS_STARTED,
                    "location": ENVIRONMENT,
                    "timestamp": start_time,
                    "fields": {
                        "status": 'init'
                    },
                    "tags": {
                        "host": EVENT_HOST,
                        "region": ENVIRONMENT,
                        "start_time": start_time,
                        "tenant": task.getProgram(),
                        "task": task.taskname,
                        "id": task.task_id
                    }
                }
                await conn.write(data, bucket=INFLUX_DATABASE)
            except Exception as e:
                logging.error(
                    f'DI: Error saving Task Execution: {e}'
                )
                print(traceback.format_exc())
