"""
NavScheduler.

Job for attaching tasks to the Scheduler.
"""
import asyncio
import locale
import os
import socket
import sys
import traceback
import uuid
import zoneinfo
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor as ThreadExecutor
from datetime import datetime
from functools import partial
from aiohttp import web
from apscheduler.events import (EVENT_JOB_ADDED, EVENT_JOB_ERROR,
                                EVENT_JOB_EXECUTED, EVENT_JOB_MAX_INSTANCES,
                                EVENT_JOB_MISSED, EVENT_JOB_SUBMITTED,
                                EVENT_SCHEDULER_SHUTDOWN,
                                EVENT_SCHEDULER_STARTED, JobExecutionEvent)
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.executors.debug import DebugExecutor
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.jobstores.base import ConflictingIdError, JobLookupError
# Jobstores
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.redis import RedisJobStore
# apscheduler library  #
# Default Scheduler:
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.combining import AndTrigger, OrTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
# Triggers
from apscheduler.triggers.interval import IntervalTrigger
# navconfig
from navconfig import config as navConfig
from navconfig.logging import logging
# asyncdb:
from asyncdb import AsyncDB
from asyncdb.exceptions import NoDataFound
from navigator.connections import PostgresPool
# Notify:
from notify import Notify
from notify.models import Actor, Chat
from notify.providers.email import Email
from querysource.types.validators import Entity

# Queue Worker Client:
from qw.client import QClient
from qw.wrappers import TaskWrapper

# dataintegration
from flowtask.conf import (
    CACHE_HOST, CACHE_PORT, DEBUG, DEFAULT_RECIPIENT,
    EMAIL_HOST, EMAIL_PASSWORD, EMAIL_PORT,
    EMAIL_USERNAME, ENABLE_JOBS, ENVIRONMENT,
    EVENT_CHAT_BOT, EVENT_CHAT_ID,
    SCHEDULER_GRACE_TIME, SCHEDULER_MAX_INSTANCES,
    SYSTEM_LOCALE, TIMEZONE, WORKER_HIGH_LIST,
    WORKER_LIST, asyncpg_url
)
from flowtask.tasks.task import Task
from flowtask.exceptions import (
    FileError, FileNotFound, NotSupported,
    TaskFailed, TaskNotFound
)
# Handler
from .handlers import SchedulerManager


# disable logging of APScheduler
logging.getLogger('apscheduler').setLevel(logging.WARNING)
logging.getLogger('apscheduler').propagate = False

if WORKER_LIST:
    QW = QClient(
        worker_list=WORKER_LIST
    )
    QW_high = QClient(
        worker_list=WORKER_HIGH_LIST
    )
else:
    QW = QClient() # auto-discovering of workers
    QW_high = QW


def getNotify(notify, **kwargs):
    args = {}
    if notify == 'telegram':
        # defining the Default chat object:
        recipient = Chat(**{"chat_id": EVENT_CHAT_ID, "name": "Navigator"})
        # send notifications to Telegram bot
        args = {
            "bot_token": EVENT_CHAT_BOT,
            **kwargs
        }
        ntf = Notify('telegram', **args)
    elif notify == 'email':
        account = {
            "host": EMAIL_HOST,
            "port": EMAIL_PORT,
            "username": EMAIL_USERNAME,
            "password": EMAIL_PASSWORD
        }
        recipient = Actor(**DEFAULT_RECIPIENT)
        ntf = Email(debug=True, **account)
    else:
        recipient = Actor(**DEFAULT_RECIPIENT)
        ntf = Notify(notify, **args)
    return [ntf, recipient]


def send_notification(event_loop, message, provider):
    asyncio.set_event_loop(event_loop)
    ntf, recipients = getNotify(provider)
    args = {
        "recipient": [recipients],
        "message": message,
    }
    if ntf.provider_type == 'email':
        args['subject'] = message
    if ntf.provider == 'telegram':
        args["disable_notification"] = True
    try:
        result = event_loop.run_until_complete(
            ntf.send(**args)
        )
        logging.debug(f'NOTIFY result: {result}')
    except Exception as err:
        logging.exception(err)


class TaskScheduler:
    def __init__(self, program, task, priority: str = 'low', **kwargs):
        self.task = task
        self.program = program
        self.priority = priority
        self.wrapper = TaskWrapper(
            program=program,
            task=task,
            ignore_results=True,
            **kwargs
        )
        self.id = uuid.uuid4()

    def running_processes(self):
        pid = os.getpid()
        return os.popen(f"ls -1 /proc/{pid}/fd | wc -l").read()

    def __call__(self, *args, **kwargs):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            processes = self.running_processes()
            logging.debug(
                f'SCHED: Starting running Processes: {processes}'
            )
        except (OSError, IOError):
            logging.exception(
                'Too many Open Files'
            )
            send_notification(
                loop,
                message="Scheduler: Too many Open Files",
                provider='telegram'
            )
            raise
        result = False
        logging.debug(
            f':::: Calling Task {self.program}.{self.task} in priority {self.priority!s}'
        )
        try:
            if self.priority == 'high':
                result = loop.run_until_complete(
                    asyncio.wait_for(
                        QW_high.queue(self.wrapper),
                        timeout=10
                    )
                )
            elif self.priority in ['low', 'None'] or self.priority is None:
                result = loop.run_until_complete(
                    asyncio.wait_for(
                        QW.queue(self.wrapper),
                        timeout=10
                    )
                )
            else:
                raise Exception(f'Unknown Priority Mode {self.priority}')
            logging.debug(
                f'SCHED: result returned by task {self.task} {result}'
            )
        except asyncio.TimeoutError:  # pragma: no cover
            logging.warning(
                f"Scheduler: Cannot add task {self.task} to Queue Worker."
            )
        finally:
            if loop.is_running():
                tasks = loop.create_task(
                    asyncio.wait(
                        asyncio.Task.all_tasks(loop),
                        timeout=10
                    )
                )
                while not tasks.done() and not tasks.cancelled():
                    pass
            processes = self.running_processes()
            logging.debug(
                f'SCHED: End Processes: {processes}'
            )
            print("Closing Loop")
            loop.close()


async def launch_task(program, task_id, loop, ENV):
    print(f'RUNNING THE TASK {program}.{task_id}')
    task = Task(
        task=task_id,
        program=program,
        loop=loop,
        ignore_results=True,
        ENV=ENV,
        debug=DEBUG
    )
    try:
        start = await task.start()
        if not start:
            logging.error(
                f'Failing Task Start: {program}.{task_id}'
            )
    except Exception as err:
        logging.error(err)
        raise TaskFailed(err) from err
    try:
        result = await task.run()
        return result
    except (NotSupported, FileNotFound, NoDataFound):
        raise
    except TaskNotFound as err:
        raise TaskNotFound(
            f'Task: {task_id}: {err!s}'
        ) from err
    except TaskFailed as err:
        raise TaskFailed(
            f'Task {task_id} failed: {err}'
        ) from err
    except FileError as err:
        raise FileError(
            f'Task {task_id}, File Not Found error: {err}'
        ) from err
    except Exception as err:
        raise TaskFailed(
            f'Error: Task {task_id} failed: {err}'
        ) from err
    finally:
        try:
            await task.close()
        except Exception as err:
            logging.error(err)


def import_from_path(path):
    """Import a module / class from a path string.
    :param str path: class path, e.g., ndscheduler.corescheduler.job
    :return: class object
    :rtype: class
    """
    components = path.split('.')
    module = __import__('.'.join(components[:-1]))
    for comp in components[1:-1]:
        module = getattr(module, comp)
    return getattr(module, components[-1])

async def time_tick(*args, **kwargs):
    print(f"Local time is: {datetime.now()}")


jobstores = {
    'default': MemoryJobStore(),
    'db': RedisJobStore(
        db=3,
        jobs_key='apscheduler.jobs',
        run_times_key='apscheduler.run_times',
        host=CACHE_HOST,
        port=CACHE_PORT
    )
}

job_defaults = {
    'coalesce': False,
    'max_instances': SCHEDULER_MAX_INSTANCES,
    'misfire_grace_time': SCHEDULER_GRACE_TIME
}


def get_function(job: dict, priority: str = 'low'):
    fn = job['job']
    t = fn['type']
    params = {}
    if job['params']:
        params = {**job['params']}
    try:
        func = fn[t]
    except KeyError as e:
        raise RuntimeError(
            f'Error getting Function on Schedule {t}'
        ) from e
    if t == 'function':
        try:
            fn = globals()[func]
            return fn
        except Exception as err:
            raise RuntimeError(
                f'Error: {err!s}'
            ) from err
    elif t == 'package':
        try:
            fn = import_from_path(func)
            return fn
        except Exception as err:
            raise RuntimeError(
                f'Error: {err!s}'
            ) from err
    elif t == 'task':
        task, program = fn['task'].values()
        if priority == 'local':
            # run in a function wrapper
            func = partial(
                launch_task,
                program,
                task
            )
            return func
        else:
            sched = TaskScheduler(program, task, priority, **params)
            sched.__class__.__name__ = f'Task({program}.{task})'
            return sched
    else:
        return None


class NavScheduler(object):
    """NavScheduler.

    Demonstrates how to use the asyncio compatible scheduler to schedule jobs.
    """
    def __init__(self, event_loop=None):
        self.db = None
        self._pool = None
        self._connection = None
        self._jobs: dict = {}
        self._loop = None
        self.scheduler = None
        self._args = None
        if event_loop:
            self._loop = event_loop
        else:
            self._loop = asyncio.new_event_loop()
        # logging
        self.logger = logging.getLogger(name='Flowtask.Scheduler')
        # asyncio scheduler
        self._timezone = zoneinfo.ZoneInfo(TIMEZONE)
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors={
                'default': AsyncIOExecutor(),
                'asyncio': AsyncIOExecutor(),
                'process': ProcessPoolExecutor(max_workers=90),
                'thread': ThreadPoolExecutor(max_workers=90),
                'debug': DebugExecutor()
            },
            job_defaults=job_defaults,
            timezone=self._timezone
        )
        # defining Locale
        try:
            locale.setlocale(locale.LC_ALL, SYSTEM_LOCALE)
        except locale.Error as e:
            self.logger.exception(e, exc_info=True)

    def setup(self, app: web.Application):
        self.db = PostgresPool(
            dsn=asyncpg_url,
            name='NavScheduler',
            startup=self.startup
        )
        self.db.configure(app, register='database') # pylint: disable=E1123
        # add the scheduler to the current app
        app['scheduler'] = self
        # add the routes:
        app.router.add_view('/api/v2/scheduler', SchedulerManager)
        app.router.add_view('/api/v2/scheduler/{job}', SchedulerManager)

    async def startup(self, app: web.Application, conn: Callable):
        """
        Scheduler Startup.
        """
        try:
            self._pool = conn
        except Exception as err:
            self.logger.exception(err)
            raise Exception(err) from err
        # auxiliary connection
        if self._pool:
            self._connection = await self._pool.acquire()
        # getting Jobs
        await self.create_jobs()
        # adding listeners
        self.add_listeners()
        self.logger.info(
            f"Scheduled Started at {datetime.now()}"
        )
        try:
            # asyncio scheduler
            self.scheduler.start()
        except Exception as err:
            raise Exception(
                f'Error Starting Scheduler {err!r}'
            ) from err
        # set Zoneinfo:
        tz = f"SET timezone TO '{TIMEZONE}'"
        await self._connection.execute(tz)


    @property
    def event_loop(self):
        return self._loop

    async def create_jobs(self):
        # First Sample Task
        self.scheduler.add_job(
            time_tick,
            IntervalTrigger(seconds=10),
            id='example_job',
            replace_existing=True,
            jobstore='default',
            executor='asyncio'
        )
        self._jobs = {}
        if ENABLE_JOBS is True:
            # Job for self-service discovering
            sql_jobs = 'SELECT * FROM troc.jobs WHERE enabled = true'
            jobs, error = await self._connection.query(sql_jobs)
        else:
            jobs = None
            error = None
        if error:
            raise Exception(
                f'[{ENVIRONMENT} - NAV Scheduler] Error getting Jobs: {error!s}')
        if jobs:
            for job in jobs:
                jitter = None
                job_id = job['job_id']
                # uid = job['job_uuid']
                if job['jitter']:
                    jitter = job['jitter']
                # function or other call
                func = get_function(job, priority=job['priority'])
                schedule_type = job['schedule_type']
                self.logger.debug(
                    f"Created new Job {job_id} with {func!s} and schedule: {schedule_type}")
                if schedule_type == 'interval':
                    t = job['schedule']
                    if job['start_date']:
                        t = {**t, **{"start_date": job['start_date']}}
                    if job['end_date']:
                        t = {**t, **{"end_date": job['end_date']}}
                    trigger = IntervalTrigger(**t)
                elif schedule_type == 'crontab':
                    t = job['schedule']['crontab']
                    trigger = CronTrigger.from_crontab(t, timezone=TIMEZONE)
                elif schedule_type == 'cron':
                    trigger = self.get_cron_params(job['schedule'])
                    if job['start_date']:
                        trigger = {**trigger,
                                   ** {"start_date": job['start_date']}}
                    if job['end_date']:
                        trigger = {**trigger, **{"end_date": job['end_date']}}
                    if jitter:
                        trigger = {**trigger, **{"jitter": jitter}}
                    trigger = CronTrigger(**trigger)
                elif schedule_type == 'date':
                    trigger = DateTrigger(
                        run_date=job['run_date'],
                        timezone=self._timezone
                    )
                elif schedule_type == 'combined':
                    t = job['schedule']
                    try:
                        jointype = t['type']
                        del t['type']
                    except KeyError:
                        jointype = 'and'
                    steps = []
                    for step, value in t.items():
                        # the expression need to be equal to Trigger Requirements
                        obj = self.get_trigger(step)
                        tg = obj(**value)
                        steps.append(tg)
                    if jointype == 'and':
                        trigger = AndTrigger(steps)
                    else:
                        trigger = OrTrigger(steps)
                ## Building Job for Scheduler:
                job_struct = {
                    'id': f'{job_id}',
                    'replace_existing': True,
                    'jobstore': job['jobstore'],
                    'executor': job['executor']
                }
                arguments = {}
                if job['params']:
                    arguments = {**job['params']}
                # agregar al args que recibe la tarea:
                arguments['loop'] = self._loop
                arguments['ENV'] = navConfig
                attributes = []
                if job['attributes']:
                    attributes = job['attributes']
                ## add this job
                if job_struct:
                    try:
                        j = self.scheduler.add_job(
                            func,
                            logger=self.logger,
                            jobstore_retry_interval=30,
                            trigger=trigger,
                            kwargs=arguments,
                            args=attributes,
                            **job_struct
                        )
                        sched = 'asyncio'
                        info = {
                            'data': job,
                            'job': j,
                            'scheduler': sched,
                            'status': 'idle'
                        }
                        self._jobs[job_id] = info
                    except ConflictingIdError as err:
                        self.logger.error(err)
                    except Exception as err:
                        self.logger.exception(err)
                else:
                    self.logger.error('Scheduler: Invalid Scheduled Job Structure')

    def add_listeners(self):
        # Asyncio Scheduler
        self.scheduler.add_listener(
            self.scheduler_status, EVENT_SCHEDULER_STARTED)
        self.scheduler.add_listener(
            self.scheduler_shutdown, EVENT_SCHEDULER_SHUTDOWN)
        self.scheduler.add_listener(self.job_success, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(
            self.job_status, EVENT_JOB_ERROR | EVENT_JOB_MISSED
        )
        # job was submitted:
        self.scheduler.add_listener(self.job_submitted, EVENT_JOB_SUBMITTED)
        # a new job was added:
        self.scheduler.add_listener(self.job_added, EVENT_JOB_ADDED)

    def job_added(self, event: JobExecutionEvent, *args, **kwargs):
        try:
            job = self.scheduler.get_job(event.job_id)
            job_name = job.name
            self.logger.debug(f'Job {job_name!s} was added.')
        except Exception:
            pass

    def get_jobs(self):
        return [
            job.id for job in self.scheduler.get_jobs()
        ]

    def get_all_jobs(self):
        return self.scheduler.get_jobs()

    def get_job(self, job_id):
        return self._jobs[job_id]

    def scheduler_status(self, event):
        print(event)
        self.logger.debug(f'[{ENVIRONMENT} - NAV Scheduler] :: Started.')
        self.logger.info(
            f'[{ENVIRONMENT} - NAV Scheduler] START time is: {datetime.now()}'
        )

    def scheduler_shutdown(self, event):
        self.logger.info(
            f'[{ENVIRONMENT}] Scheduler Stopped at: {datetime.now()}'
        )

    def job_success(self, event: JobExecutionEvent):
        """Job Success.

        Event when a Job was executed successfully.

        :param apscheduler.events.JobExecutionEvent event: job execution event
        """
        job_id = event.job_id
        job = self.scheduler.get_job(job_id)
        try:
            saved_job = self._jobs[job_id]
        except KeyError:
            # Job is missing from the Job Store.
            return False
        saved_job['status'] = 'Success'
        job_name = job.name
        self.logger.info(
            f'[Schedulder - {ENVIRONMENT}]: {job_name} with id {event.job_id!s} was executed successfully @ {event.scheduled_run_time!s}'
        )
        # saving into Database
        event_loop = asyncio.new_event_loop()
        fn = partial(
            self.save_db_event,
            event_loop=event_loop,
            event=event,
            job=job
        )
        try:
            with ThreadExecutor(max_workers=1) as pool:
                event_loop.run_in_executor(pool, fn)
        finally:
            event_loop.close()

    def job_status(self, event: JobExecutionEvent):
        """React on Error events from scheduler.

        :param apscheduler.events.JobExecutionEvent event: job execution event.

        TODO: add the reschedule_job
        scheduler = sched.scheduler #it returns the native apscheduler instance
        scheduler.reschedule_job('my_job_id', trigger='cron', minute='*/5')

        """
        job_id = event.job_id
        job = self.scheduler.get_job(job_id)
        saved_job = self._jobs[job_id]
        job_name = job.name
        scheduled = event.scheduled_run_time
        stack = event.traceback
        if event.code == EVENT_JOB_MISSED:
            saved_job['status'] = 'Missed'
            self.logger.warning(
                f"[{ENVIRONMENT} - NAV Scheduler] Job {job_name} was missed for scheduled run at {scheduled}")
            message = f'⚠️ :: [{ENVIRONMENT} - NAV Scheduler] Job {job_name} was missed for scheduled run at {scheduled}'
        elif event.code == EVENT_JOB_ERROR:
            saved_job['status'] = 'Error'
            self.logger.error(
                f"[{ENVIRONMENT} - NAV Scheduler] Job {job_name} scheduled at {scheduled!s} failed with Exception: {event.exception!s}"
            )
            message = f'🛑 :: [{ENVIRONMENT} - NAV Scheduler] Job **{job_name}** scheduled at {scheduled!s} failed with Error {event.exception!s}'
            if stack:
                self.logger.exception(
                    f"[{ENVIRONMENT} - NAV Scheduler] Job {job_name} id: {job_id!s} StackTrace: {stack!s}"
                )
                message = f'🛑 :: [{ENVIRONMENT} - NAV Scheduler] Job **{job_name}**:**{job_id!s}** failed with Exception {event.exception!s}'
            # send a Notification error from Scheduler
        elif event.code == EVENT_JOB_MAX_INSTANCES:
            saved_job['status'] = 'Not Submitted'
            self.logger.exception(
                f"[{ENVIRONMENT} - NAV Scheduler] Job {job_name} could not be submitted. Maximum number of running instances was reached."
            )
            message = f'⚠️ :: [{ENVIRONMENT} - NAV Scheduler] Job **{job_name}** was missed for scheduled run at {scheduled}'
        else:
            saved_job['status'] = 'Exception'
            # will be an exception
            message = f'🛑 :: [{ENVIRONMENT} - NAV Scheduler] Job {job_name}:{job_id!s} failed with Exception {stack!s}'
            # send a Notification Exception from Scheduler
        # send notification:
        event_loop = asyncio.new_event_loop()
        fn = partial(
            send_notification,
            event_loop=event_loop,
            message=message,
            provider='telegram'
        )
        saved = partial(
            self.save_db_event,
            event_loop=event_loop,
            event=event,
            job=job
        )
        # sending function coroutine to a thread
        try:
            with ThreadExecutor(max_workers=1) as pool:
                event_loop.run_in_executor(pool, saved)
                event_loop.run_in_executor(pool, fn)
        finally:
            event_loop.close()

    def save_db_event(self, event_loop, event, job):
        asyncio.set_event_loop(event_loop)
        state = Entity.escapeString(event.exception)
        trace = Entity.escapeString(event.traceback)
        if event.code == EVENT_JOB_MISSED:
            status = 3
        elif event.code == EVENT_JOB_ERROR:
            status = 2
        elif event.code == EVENT_JOB_MAX_INSTANCES:
            status = 4
        else:
            state = 'null'
            trace = 'null'
            status = 1
        status = {
            'last_exec_time': event.scheduled_run_time,
            'next_run_time': job.next_run_time,
            'job_state': state,
            'job_status': status,
            'traceback': trace,
            'job_id': event.job_id
        }
        try:
            result = event_loop.run_until_complete(
                self.update_task_status(event_loop, status)
            )
            if isinstance(result, Exception):
                self.logger.exception(result)
        except Exception as err:
            print(err)
            self.logger.exception(err)

    async def update_task_status(self, event_loop, status):
        # TODO: migrate to Prepared statements
        asyncio.set_event_loop(event_loop)
        sql = """UPDATE troc.jobs
        SET last_exec_time='{last_exec_time}', next_run_time='{next_run_time}',
        job_status='{job_status}', job_state={job_state}, traceback={traceback}
        WHERE job_id = '{job_id}';"""
        sentence = sql.format(**status)
        result = None
        print('SQL ', sentence)
        options = {
            "server_settings": {
                'application_name': 'Nav-Scheduler',
                'client_min_messages': 'notice',
                'max_parallel_workers': '12',
                'jit': 'off'
            }
        }
        conn = AsyncDB('pg', dsn=asyncpg_url, loop=event_loop, **options)
        try:
            async with await conn.connection() as conn:
                result, error = await conn.execute(sentence)
                if error:
                    self.logger.error(error)
            return result
        except Exception as err:
            print(err)
            self.logger.exception(err)

    def job_submitted(self, event):
        try:
            job = self.scheduler.get_job(event.job_id)
        except (JobLookupError, Exception) as err:
            raise Exception(
                f'Scheduler: There is no such Job Scheduled {err}'
            )
        job_name = job.name
        self.logger.info(
            f'Sched: Job {job_name} with id {event.job_id!s} was submitted @ {datetime.now()}')

    def get_stacktrace(self):
        """Returns the full stack trace."""

        type_, value_, traceback_ = sys.exc_info()
        return ''.join(traceback.format_exception(type_, value_, traceback_))

    def get_hostname(self):
        """Returns the host name."""
        return socket.gethostname()

    def get_pid(self):
        """Returns the process ID"""
        return os.getpid()

    async def start(self):
        try:
            # asyncio scheduler
            self.scheduler.start()
        except Exception as err:
            raise Exception(f'Error Starting Scheduler {err!r}')

    async def shutdown(self, app: web.Application):
        try:
            # self.backscheduler.shutdown(wait=True)
            self.scheduler.shutdown(wait=True)
            if self._connection:
                await self._pool.release(self._connection)
            await self.db.shutdown(app)
        except Exception as err:
            self.logger.exception(f'Error on Scheduler Shutdown {err!r}')

    def get_cron_params(self, expression):
        trigger = {
            "year": "*",
            "month": "*",
            "day": "*",
            "week": "*",
            "day_of_week": "*",
            "hour": "*",
            "minute": "*",
            "second": "0"
        }
        return {**trigger, **expression}

    def get_cron_strings(self, expression):
        """Returns cron strings.
        :param dict expression: an array of cron structures.
        :return: cron strings
        :rtype: dict
        """
        trigger = expression['cron']
        return {
            'month': str(trigger[1]),
            'day': str(trigger[2]),
            'week': str(trigger[3]),
            'day_of_week': str(trigger[4]),
            'hour': str(trigger[5]),
            'minute': str(trigger[6])
        }

    def get_trigger(self, expression):
        if expression == 'cron' or expression == 'crontab':
            return CronTrigger
        elif expression == 'date':
            return DateTrigger
        elif expression == 'interval':
            return IntervalTrigger
        else:
            self.logger.exception(f'Wrong Trigger type: {expression}')
            return None
