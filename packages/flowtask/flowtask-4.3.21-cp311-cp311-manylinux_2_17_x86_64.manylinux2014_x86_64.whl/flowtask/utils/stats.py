"""TaskMonitor.

Collect and saves stats for execution of tasks.
"""
import os
import sys
import asyncio
import logging
from datetime import datetime
import time
from statistics import mean
from contextlib import suppress
from typing import (
    List,
    Any
)
from psutil import virtual_memory, cpu_percent, Process


class StepMonitor:
    def __init__(self, name, parent: "TaskMonitor" = None) -> None:
        self.name = name
        self.executed_at: datetime = datetime.now()
        self.stats: dict = {}
        self.traceback: str = None
        self._parent: Any = parent

    def add_metric(self, key, value) -> None:
        self.stats[key] = value

    def stacktrace(self, trace: str) -> None:
        self.traceback = trace

    def parent(self):
        return self._parent

    def __str__(self) -> str:
        trace = ''
        if self.traceback:
            trace = f"StackTrace: <{self.traceback!s}>\n"
        stat = (
            f'{self.name}:\n'
            f'Executed At: {self.executed_at}:\n'
            f"<{self.stats!r}>\n"
            f"{trace!s}\n"
        )
        return stat


class TaskMonitor:
    def __init__(self, name: str, program: str, task_id: str) -> None:
        self.task_name = name
        self.task_id = task_id
        self._started: bool = False
        self.traceback = None
        self.stats: dict = {}
        self.user: str = None
        self.steps: List[StepMonitor] = []
        self.executed_at: datetime = datetime.now()
        self.start_time: float = 0
        self.finish_time: float = 0
        self.duration: float = 0
        self._sampling_task: asyncio.Task
        self.program: str = program
        # CPU and RAM stats:
        self.baseline_cpu: float = 0
        self.baseline_ram: float = 0
        self._cpu_usage_data: list = []
        self._ram_usage_data: list = []
        self._memory_info: list = []
        # returned values of Stats
        self.max_cpu_used: float = 0
        self.avg_cpu_used: float = 0
        self.max_ram_used: float = 0
        self.avg_ram_used: float = 0
        self.memory_usage: float = 0
        ## TODO: passing User information:
        if sys.stdin and sys.stdin.isatty():
            self.exec_type = 'console'
            try:
                self.user = os.environ.get('USER')
            except Exception:
                self.user = os.environ.get('USERNAME')
        else:
            # was dispatched from code
            try:
                if 'qw' in sys.argv[0]:
                    self.exec_type = 'worker'
                else:
                    self.exec_type = 'task'
            except IndexError:
                self.exec_type = 'code'
                self.user = os.getlogin()
        print(f'Execution Mode: {self.exec_type}')

    def __str__(self) -> str:
        steps = "\n".join([f"{step!s}" for step in self.steps])
        if steps:
            steps = f"Steps: \n{steps!s}\n"
        stat = (
            f'Task: {self.task_name}\n'
            f'ID: {self.task_id}\n'
            f"< {self.stats!r} >\n"
            f"{steps!s}"
        )
        return stat

    def to_json(self) -> str:
        steps = {}
        for step in self.steps:
            steps[step.name] = {
                "executed_at": step.executed_at,
                **step.stats
            }
        stat = {
            "Task": self.task_name,
            "program": self.program,
            "task_name": f"{self.program}.{self.task_name}",
            "ID": self.task_id,
            **self.stats,
            "steps": {
                **steps
            }
        }
        return stat

    def add_step(self, step: StepMonitor) -> None:
        self.steps.append(step)

    async def start_timing(self):
        self.start_time = time.time()

    async def end_timing(self):
        self.finish_time = time.time()
        self.duration = self.finish_time - self.start_time

    def stacktrace(self, trace: str) -> None:
        self.traceback = trace

    def is_started(self) -> bool:
        return self._started


    async def cpu_percent(self, *args, interval = None, **kwargs):
        if interval is not None and interval > 0.0:
            cpu_percent(*args, **kwargs)
            await asyncio.sleep(interval)
        return cpu_percent(*args, **kwargs)

    async def _get_current_state(self, interval: float = 0.4):
        """_get_current_state.
            Get the Current state of System, will be collected async every tick.
        Args:
            interval (float, optional): interval of collecting information. Defaults to 0.2.
        Raises:
            err: _description_
        """
        while True:
            try:
                self._cpu_usage_data.append(await self.cpu_percent(interval=0))
                self._ram_usage_data.append(virtual_memory().percent)
                self._memory_info.append(
                    Process().memory_info().rss / 1048576
                )
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                return True
            except Exception as err:
                logging.exception(
                    f'Can\'t, Collect CPU/RAM metrics due to error: {err}'
                )

    async def start(self, interval: float = 0.4) -> bool:
        try:
            # check if not started:
            if not self._started:
                self._started = True
                await self.start_timing()
                # Start task to call func periodically:
                self._sampling_task = asyncio.ensure_future(
                    self._get_current_state(interval)
                )
            # is started
        except Exception as err:
            logging.exception(
                f'Task Monitor Failed to Start, error: {err}'
            )

    async def _calculate_stats(self):
        if self._cpu_usage_data:
            self.max_cpu_used = max(self._cpu_usage_data)
            self.avg_cpu_used = mean(self._cpu_usage_data)
            self.max_ram_used = max(self._ram_usage_data)
            self.avg_ram_used = mean(self._ram_usage_data)
            self.memory_usage = mean(self._memory_info)

    async def stop(self) -> dict:
        try:
            # Check is sampling is happening
            if self._started:
                # Stopping Monitor.
                self._started = False
                # Stop task and await it stopped:
                self._sampling_task.cancel()
                with suppress(asyncio.CancelledError):
                    await self._sampling_task
                # Stop the clock, making calculations
                await self.end_timing()
                await self._calculate_stats()
                self.stats.update(
                    {
                        "executed_at": f"{self.executed_at:%Y-%m-%d %H:%M}",
                        "duration": f"{self.duration:.5f}",
                        "max_cpu": round(float(self.max_cpu_used), 2),
                        "avg_cpu": round(float(self.avg_cpu_used), 2),
                        "max_ram": round(float(self.max_ram_used), 2),
                        "avg_ram": round(float(self.avg_ram_used), 2),
                        "memory_usage": self.memory_usage,
                        "exec_type": self.exec_type,
                        "user": self.user
                    }
                )
                return self.stats
            else:
                return {}
        except Exception as err:
            logging.exception(
                f'Task Monitor Failed to Stop, due to: {err}'
            )
