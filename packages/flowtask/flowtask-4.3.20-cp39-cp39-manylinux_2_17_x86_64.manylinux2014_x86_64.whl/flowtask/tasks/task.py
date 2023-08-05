import asyncio
import traceback
from collections.abc import Callable
from asyncdb.exceptions import (
    NoDataFound,
    ProviderError
)
# DataIntegration
from flowtask.components import SkipErrors
from flowtask.utils.stats import StepMonitor
from flowtask.models import (
    TaskState
)
from flowtask.exceptions import (
    TaskFailed,
    TaskDefinition,
    TaskError,
    TaskParseError,
    TaskNotFound,
    NotSupported,
    ComponentError,
    DataNotFound,
    FileNotFound,
    FileError
)
from flowtask.tasks.pile import TaskPile
from flowtask.utils import cPrint, check_empty, AttrDict
from .abstract import AbstractTask


class Task(AbstractTask):
    """
    Task.

        Object contain a Data-Integration Task.
    """
    def __init__(
        self,
        task_id: str = None,
        task: str = None,
        program: str = None,
        loop: asyncio.AbstractEventLoop = None,
        parser: Callable = None,
        worker: Callable = None,
        **kwargs
    ) -> None:
        self._pile = None
        self._steps = None
        self._vars = None
        super(Task, self).__init__(
            task_id=task_id,
            task=task,
            program=program,
            loop=loop,
            parser=parser,
            **kwargs
        )
        self._taskname = task
        self._conditions = {}
        self._attrs = {}
        self.ignore_steps = []
        self.run_only = []
        self._stepattrs = {}
        self._kwargs = {}
        self._variables = {}
        self._masks = {}
        if not self._taskname:
            raise TaskError(
                'Missing Task Name, \
                    HINT: add --task (in command line) or parameter "task" with a task name'
            )
        # change root-level attributes on fly
        if parser:
            self._attrs = parser.attributes
        try:
            attrs = kwargs['attributes']
            del kwargs['attributes']
            self._attrs = {**self._attrs, **attrs}
        except KeyError:
            pass
        # for component-based attributes (ex: --DownloadFromIMAP_1:host)
        if parser:
            self._stepattrs = parser.stepattrs
        try:
            steps = kwargs['steps']
            del kwargs['steps']
            if steps:
                self._stepattrs = {**self._stepattrs, **steps}
        except KeyError:
            pass
        try:
            self.is_subtask = kwargs['is_subtask']
            del kwargs['is_subtask']
        except KeyError:
            self.is_subtask: bool = False
        # ignoring components in task execution.
        if parser:
            self.ignore_steps = self._options.ignore
        if not self.ignore_steps:
            try:
                self.ignore_steps = kwargs['ignore_steps']
                del kwargs['ignore_steps']
            except KeyError:
                self.ignore_steps = []
        # list of "run only" components:
        if parser:
            self.run_only = self._options.run_only
        try:
            self.run_only = kwargs['run_only']
            del kwargs['run_only']
        except KeyError:
            pass
        # variables: can be passed between components as reusable values.
        if parser:
            self._variables = self._options.variables
        try:
            variables = kwargs['variables']
            del kwargs['variables']
            if isinstance(variables, dict):
                self._variables = {**self._variables, **variables}
        except KeyError:
            pass
        self.logger.debug(f'CURRENTLY NEW Variables: {self._variables}')
        # masks: replacing masks with values or even new functions
        if parser:
            self._masks = self._options.masks
        # conditions: replacing conditions (on components with conditions support)
        if parser:
            self._conditions = self._options.conditions
            self._args = self._options.args
        try:
            conditions = kwargs['conditions']
        except KeyError:
            conditions = {}
        self._conditions = {**self._conditions, **conditions}
        # print(f'CURRENTLY NEW CONDS: {self._conditions}')
        self.worker = worker
        if kwargs:
            # remain args go to kwargs:
            self._kwargs = {**kwargs}
        self.logger.debug(f':: Launch Task {self._taskname} with id: {self.task_id}')
        self._state = TaskState.PENDING
        self._events.onTaskInit(
            message=f":: Task Pending for Execution: {self._taskname}, program: {self._program}",
            task=self
        )

    async def close(self):
        """close.

            Closing the remaining connections.
        """
        if self.is_subtask is False:
            await super(Task, self).close()
        self._pile = None
        self._steps = None
        self._args = None

    @property
    def variables(self):
        return self._vars

    @property
    def taskname(self):
        return self._taskname

    def __repr__(self) -> str:
        return f"{self._program}.{self._taskname}"

    async def prepare(self):
        if self._task:
            # calling steps
            try:
                self._pile = TaskPile(self._task, program=self._program)
                return True
            except (KeyError, TaskDefinition) as err:
                raise TaskDefinition(
                    f"Bad Task Definition: {err!s}"
                ) from err
            except Exception as err:
                raise TaskDefinition(
                    f"Task Exception {self._program}.{self._taskname}: {err!s}"
                ) from err
        else:
            raise NotSupported(
                f'DI: Unknown Task Type: {self._program}.{self._taskname}'
            )

    def get_component(self, step, prev):
        step_name = step.name
        if self.enable_stat is True:
            stat = StepMonitor(name = step_name, parent = self.stat)
            self.stat.add_step(stat)
        else:
            stat = None
        params = step.params()
        params['program'] = self._program
        params['ENV'] = self._env
        # params:
        params['params'] = self._params
        # parameters
        params['parameters'] = self._parameters
        # useful to change variables in set var components
        params['_vars'] = self._kwargs
        # variables dictionary
        try:
            variables = params['variables']
        except KeyError:
            variables = {}
        if prev:
            variables = {**variables, **prev.variables}
        params['variables'] = {**self._variables, **variables}
        params['_masks'] = self._masks # override mask value
        try:
            arguments = params['arguments']
        except KeyError:
            arguments = []
        if not self._arguments:
            self._arguments = []
        params['arguments'] = arguments + self._arguments
        # argument list for components (or tasks) that need argument lists
        params['_args'] = self._args
        # for components with conditions, we can add more conditions
        try:
            conditions = params['conditions']
        except KeyError:
            conditions = {}
        params['conditions'] = {**conditions, **self._conditions}
        # attributes only usable component-only
        if step_name in self._stepattrs:
            # this can rewrite attributes for steps
            newattrs = self._stepattrs[step_name]
            self._attrs = {**self._attrs, **newattrs}
        # will be a dictionary with ComponentName: parameter
        params['attributes'] = self._attrs
        # the current Pile of components
        params['TaskPile'] = self._pile
        params['debug'] = self._debug
        params['template'] = self._template
        params['argparser'] = self._argparser
        # the current in-memory connector
        if self._memory:
            params['memory'] = self._memory
        component = None
        component = step.component
        # get dependency
        depends = step.getDepends(prev)
        if 'TaskPile' in params['parameters']:
            del params['parameters']['TaskPile']
        try:
            job = component(
                job=depends,
                loop=self._loop,
                stat=stat, # stats object
                **params
            )
            self.logger.debug(f'Task: Loaded Component {job}')
            job.TaskName = step_name
            return job
        except Exception as err:
            print(traceback.print_exc())
            raise ComponentError(
               f"DI: Component Error on {self._taskname}, \
                   Component: {step_name} error: {err}"
            ) from err

    async def start(self):
        # starting a Task
        await super(Task, self).start()
        # Open Task:
        try:
            self._task = await self.taskstore.open_task(
                self._taskname
            )
            if not self._task:
                raise TaskNotFound(
                    f'Task Missing or empty: {self._taskname}'
                )
        except TaskParseError as e:
            self._state = TaskState.EXCEPTION
            self._events.onTaskError(
                message=f'{e!s}',
                component=self._taskname,
                task=self,
                status='parse error'
            )
            raise TaskParseError(
                f'Parse Error: {e}'
            ) from e
        except TaskNotFound as e:
            raise TaskNotFound(
                f'Error on Task {self._taskname}, task not found'
            ) from e
        except Exception as err:
            raise TaskNotFound(
                f'Unknown Error on Task: {self._taskname}, error: {err}'
            ) from err
        # task is loaded, we need to check syntax.
        try:
            self.check_syntax(self._task)
        except TaskParseError as ex:
            self._state = TaskState.EXCEPTION
            self._events.onTaskError(
                message=f'{ex}',
                component=self._taskname,
                task=self,
                status='Task parsing error'
            )
            raise TaskParseError(
                f'Syntax Error on Task {self._taskname}: {ex}'
            ) from ex
        # can prepare the task before run.
        try:
            self._task = AttrDict(self._task)
            if 'timezone' in self._task:
                # re-set timezone based on Task parameter
                self.set_timezone(self._task.timezone)
            await self.prepare()
            return True
        except TaskDefinition as e:
            raise TaskDefinition(
                f"Task Definition error: {e}"
            ) from e
        except NotSupported:
            raise
        except Exception as err:
            raise TaskError(
                f"Task Error {self._taskname}.{self._program}: {err!s}"
            ) from err



    async def run(self):
        # run Task and returning the result.
        result = None
        comp = None
        prev = None
        _exit = False
        failed: list = []
        task_name = self._task['name']
        try:
            print('==== ON TASK RUNNING === ')
            self._state = TaskState.RUNNING
            self._events.onTaskRunning(
                message=f":: Task Running: {self._taskname}, program: {self._program}",
                task=self
            )
        except Exception as err:  # pytest: disable=W0718
            self.logger.error(
                f'Failed to set Running status on task {self._taskname}, {err}'
            )
        for step in self._pile:
            cPrint(f'LOADED STEP: {step.name}', level = 'DEBUG')
            step_name = step.name
            if step_name in self.ignore_steps:
                # we can ignore this component for execution
                continue
            if len(self.run_only) > 0:
                # we only need to run the existing list of components
                if step_name not in self.run_only:
                    continue
            prev = comp
            try:
                comp = self.get_component(step, prev)
                step.setStep(comp) # put the Component initialized in the Pile.
            except Exception as err:
                self._state = TaskState.STOPPED
                trace = traceback.format_exc()
                self._events.onTaskFailure(
                    message=f'{err!s}',
                    component=self._taskname,
                    task=self,
                    status='failure',
                    stacktrace=trace
                )
                raise ComponentError(
                    f"Error Getting Component {step_name}, error: {err}"
                ) from err
            if self._debug:
                cPrint(
                    f':: Running Component {step_name} from Task {task_name}', level='INFO'
                )
                self.logger.debug(
                    f':: Running Component {step_name} from Task {task_name}'
                )
            # try START
            start = getattr(comp, 'start')
            parameters = comp.user_params()
            try:
                if callable(start):
                    if asyncio.iscoroutinefunction(start):
                        st = await comp.start(**parameters)
                    else:
                        st = comp.start()
                    if st is False:
                        self._state = TaskState.STOPPED
                        self._events.onTaskError(
                            message=f'Start returns False: {err!s}',
                            component=self._taskname,
                            task=self,
                            status='error'
                        )
                        raise TaskFailed(
                            f"DI: Cannot Start Component {step_name}, error: {err}"
                        )
                else:
                    self._state = TaskState.STOPPED
                    raise TaskFailed(
                        f"DI: Error running Start on {step_name}"
                    )
            except (NoDataFound, DataNotFound):
                self._state = TaskState.NOT_FOUND
                raise
            except FileNotFound as ex:
                self._state = TaskState.NOT_FOUND
                self._events.onFileNotFound(
                    message=f'{ex!s}',
                    component=self._taskname,
                    task=self,
                    status='error'
                )
                raise
            except FileError:
                self._state = TaskState.ERROR
                self._events.onTaskFileError(
                    message=f'{err!s}',
                    component=self._taskname,
                    task=self,
                    status='error'
                )
                raise
            except (ProviderError, ComponentError, NotSupported) as err:
                self._state = TaskState.ERROR
                self._events.onTaskError(
                    message=f'{err!s}',
                    component=self._taskname,
                    task=self,
                    status='error'
                )
                raise NotSupported(
                    f"Error on Starting Component {step_name}, error: {err}"
                ) from err
            except Exception as err:
                self._state = TaskState.EXCEPTION
                trace = traceback.format_exc()
                self._events.onTaskFailure(
                    message=f'{err!s}',
                    component=self._taskname,
                    task=self,
                    status='failure',
                    stacktrace=trace
                )
                raise TaskFailed(
                    f"DI: Exception on Start Component {step_name}, Error: {err!s}"
                ) from err
            try:
                run = getattr(comp, 'run', None)
                if asyncio.iscoroutinefunction(run):
                    result = await comp.run()
                elif callable(run):
                    result = comp.run()
                else:
                    raise TaskFailed(
                        f"DI: Component {step_name} is not callable"
                    )
                # close operations
                close = getattr(comp, 'close', None)
                if asyncio.iscoroutinefunction(close):
                    await comp.close()
                else:
                    comp.close()
                if check_empty(result):
                    if comp.skipError == SkipErrors.SKIP:
                        print(f'::: SKIPPING Error on {step_name} :::: ')
                        failed.append(comp)
                        _exit = False
                        continue
                    failed.append(comp)
                    _exit = True
                    break
            except (NoDataFound, DataNotFound) as err:
                # its a data component a no data was found
                if comp.skipError == SkipErrors.SKIP:
                    failed.append(comp)
                    self.logger.debug(f'SKIP Failed Component: {comp!r}')
                    # can skip error for this component
                    continue
                self._state = TaskState.DONE_WITH_NODATA
                self._events.onDataNotFound(
                    message=f'No Found: {err}',
                    result=result,
                    component=self._taskname,
                    task=self,
                    status='not_found'
                )
                raise
            except FileNotFound as err:
                if comp.skipError == SkipErrors.SKIP:
                    failed.append(comp)
                    self.logger.debug(f'SKIP Failed Component: {comp!r}')
                    comp = prev
                    # can skip error for this component
                    continue
                self._state = TaskState.NOT_FOUND
                self._events.onFileNotFound(
                    message=f'File Not Found: {err}',
                    result=result,
                    component=self._taskname,
                    task=self,
                    status='not_found'
                )
                raise
            except FileError as err:
                self._state = TaskState.ERROR
                if comp.skipError == SkipErrors.SKIP:
                    failed.append(comp)
                    self.logger.debug(f'SKIP Failed Component: {comp!r}')
                    comp = prev
                    # can skip error for this component
                    continue
                self._state = TaskState.ERROR
                self._events.onTaskFileError(
                    message=f'File Error: {err}',
                    result=result,
                    component=self._taskname,
                    task=self,
                    status='file_error'
                )
                raise
            except (ProviderError, ComponentError, NotSupported) as err:
                self._state = TaskState.ERROR
                self._events.onTaskError(
                    message=f'{err!s}',
                    component=self._taskname,
                    task=self,
                    status='error'
                )
                if comp.skipError == SkipErrors.SKIP:
                    # can skip error for this component
                    failed.append(comp)
                    self.logger.debug(f'SKIP Failed Component: {comp!r}')
                    empty = check_empty(comp.output())
                    if empty:
                        # avoid when failed, lost the chain of results:
                        others = comp.previous
                        if isinstance(others, list):
                            previous = others[0]
                            comp.result = previous.output()
                        else:
                            comp.result = others.output()
                    _exit = False
                    continue
                else:
                    raise TaskFailed(
                        f"Error running Component {step_name}, error: {err}"
                    ) from err
            except Exception as err:
                trace = getattr(err, 'payload', None)
                if not trace:
                    trace = traceback.format_exc()
                try:
                    self.stat.stacktrace(trace)
                finally:
                    pass
                self._state = TaskState.EXCEPTION
                self._events.onTaskFailure(
                    message=f'{err!s}',
                    component=self._taskname,
                    task=self,
                    status='failure',
                    stacktrace=trace
                )
                raise TaskFailed(
                    f"Generic Component Error on {step_name}, error: {err}, {err.__class__}"
                ) from err
            self._variables = comp.variables # passing variables between components
        try:
            # stop stats:
            if self.enable_stat is True:
                await self.stat.stop()
        except Exception as err:
            self.logger.error(err)
        # ending the pile:
        self._pile = []
        del self._pile
        if _exit is True:
            # TODO: checking the failed list for returning errors.
            return False
        else:
            if check_empty(result):
                if self.is_subtask is False:
                    self._state = TaskState.DONE_WITH_NODATA
                    # mark data not found, is a warning
                    self._events.onDataNotFound(
                        message=f'No Found: {err}',
                        result=result,
                        component=self._taskname,
                        task=self
                    )
                else:
                    self._state = TaskState.DONE_WITH_NODATA
            else:
                if self.is_subtask is False:
                    # avoid firing onTaskDone when is a subtask
                    self._state = TaskState.DONE
                    self._events.onTaskDone(
                        message=f":: Task Ended: {self._taskname}, program: {self._program}",
                        result=result,
                        task=self
                    )
            if self._ignore_results is True:
                return True
            else:
                return result


    async def run_dry(self):
        # run Task and returning the result.
        comp = None
        prev = None
        _exit = False
        task_name = self._task['name']
        cPrint(
            f"::: Running Task {task_name} ::: ", level = 'INFO'
        )
        for step in self._pile:
            cPrint(f'LOAD STEP: {step.name}', level = 'DEBUG')
            step_name = step.name
            if step_name in self.ignore_steps:
                # we can ignore this component for execution
                continue
            if len(self.run_only) > 0:
                # we only need to run the existing list of components
                if step_name not in self.run_only:
                    continue
            prev = comp
            try:
                comp = self.get_component(step, prev)
                # put the Component initialized on the Pile.
                step.setStep(comp)
            except Exception as err:
                raise ComponentError(
                    f"Error Getting Component {step_name}, error: {err}"
                ) from err
            if self._debug:
                cPrint(
                    f':: Running Component {step_name} from Task {task_name}', level='INFO'
                )
                self.logger.debug(
                    f':: Running Component {step_name} from Task {task_name}'
                )
            # try START
            start = getattr(comp, 'start')
            try:
                if callable(start):
                    if asyncio.iscoroutinefunction(start):
                        st = await comp.start()
                    else:
                        st = comp.start()
            except Exception as err:
                self.logger.debug(err, stack_info=False)
            try:
                # close operations
                close = getattr(comp, 'close', None)
                if asyncio.iscoroutinefunction(close):
                    await comp.close()
                else:
                    comp.close()
            except Exception as err:
                raise TaskFailed(
                    f"DI: Exception on Close Component {step_name}, Error: {err!s}"
                ) from err

    def plot(self) -> None:
        self._pile.plot_task()
