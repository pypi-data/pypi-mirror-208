import asyncio
from collections.abc import Callable
from pathlib import PurePath
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from aiofile import AIOFile
from asyncdb.drivers.pg import pg
from asyncdb.exceptions import (
    StatementError,
    DataError
)
from navigator.conf import (
    DB_STATEMENT_TIMEOUT,
    DB_SESSION_TIMEOUT,
    DB_IDLE_TRANSACTION_TIMEOUT,
    DB_KEEPALIVE_IDLE
)
from navconfig.conf import asyncpg_url
from navconfig.logging import logging
from flowtask.exceptions import (
    ComponentError,
    FileError
)
from flowtask.utils import SafeDict
from settings.settings import TASK_PATH
from .abstract import DtComponent


class ExecuteSQL(DtComponent):
    """
    ExecuteSQL

    Overview

            Does not support mutually exclusive data sources: query,file sql.
            The ExecuteSQL only does WARNING if it fails

        .. table:: Properties
        :widths: auto


    +--------------+----------+-----------+-------------------------------------------------------+
    | Name         | Required | Summary                                                           |
    +--------------+----------+-----------+-------------------------------------------------------+
    | use_template |   Yes    | Pass the content of the SQL through a Jinja2 template processor.  |
    |              |          | Receive component variables                                       |
    +--------------+----------+-----------+-------------------------------------------------------+
    | multi        |   Yes    | Is True, there are multiple queries. to execute (query list)      |
    +--------------+----------+-----------+-------------------------------------------------------+


    Return the list of arbitrary days

    """
    def __init__(
            self,
            loop: asyncio.AbstractEventLoop = None,
            job: Callable = None,
            stat: Callable = None,
            **kwargs
    ):
        self.tablename: str = ''
        self.schema: str = ''
        self._connection: Callable = None
        try:
            self.multi = bool(kwargs['multi'])
            del kwargs['multi']
        except KeyError:
            self.multi = False
        try:
            self.use_template: bool = bool(kwargs['use_template'])
            del kwargs['use_template']
        except KeyError:
            self.use_template: bool = False
        super(ExecuteSQL, self).__init__(
            loop=loop,
            job=job,
            stat=stat,
            **kwargs
        )

    def close(self):
        """Closing Database Connection."""

    async def open_sqlfile(self, file: PurePath, **kwargs) -> str:
        if file.exists() and file.is_file():
            content = None
            # open SQL File:
            async with AIOFile(file, 'r+') as afp:
                content = await afp.read()
                # check if we need to replace masks
            content = self.mask_replacement(
                content
            )
            if self.use_template is True:
                content = self._templateparser.from_string(content, kwargs)
            return content
        else:
            raise FileError(
                f'ExecuteSQL: Missing SQL File: {file}'
            )

    async def start(self, **kwargs):
        """Start Component"""
        if self.previous:
            self.data = self.input
        # check if sql comes from a filename:
        if hasattr(self, 'file_sql'):
            self.sql = []
            qs = []
            if isinstance(self.file_sql, str):
                qs.append(self.file_sql)
            elif isinstance(self.file_sql, list):
                qs = self.file_sql
            else:
                raise ComponentError(
                    'ExecuteSQL: Unknown type for *file_sql* attribute.'
                )
            for fs in qs:
                file_path = TASK_PATH.joinpath(self._program, 'sql', fs)
                try:
                    sql = await self.open_sqlfile(file_path)
                    self.sql.append(sql)
                except Exception as err:
                    raise Exception from err
        if hasattr(self, 'pattern'):
            # need to parse variables in SQL
            pattern = self.pattern
            sql = self.sql
            self.sql = []
            try:
                variables = {}
                for field, val in pattern.items():
                    variables[field] = self.getFunc(val)
            except (TypeError, AttributeError) as err:
                logging.error(err)
            # replace all ocurrences on SQL
            try:
                # TODO: capture when sql is a list of queries
                sql = sql.format_map(SafeDict(**variables))
                # Replace variables
                for val in self._variables:
                    if isinstance(self._variables[val], list):
                        if isinstance(self._variables[val], int):
                            self._variables[val] = ', '.join(self._variables[val])
                        else:
                            self._variables[val] = ', '.join("'{}'".format(v) for v in self._variables[val])
                    sql = sql.replace('{{{}}}'.format(str(val)), str(self._variables[val]))
                self.sql.append(sql)
            except Exception as err:
                logging.error(err)
        if hasattr(self, 'sql'):
            if isinstance(self.sql, str):
                self.sql = [self.sql]
        # Replace variables
        for val in self._variables:
            sqls = []
            for sql in self.sql:
                if isinstance(self._variables[val], list):
                    if isinstance(self._variables[val], int):
                        self._variables[val] = ', '.join(self._variables[val])
                    else:
                        self._variables[val] = ', '.join("'{}'".format(v) for v in self._variables[val])
                sql = sql.replace(
                    '{{{}}}'.format(str(val)),
                    str(self._variables[val])
                )
                sqls.append(sql)
            self.sql = sqls
        return True

    def get_connection(self, event_loop: asyncio.AbstractEventLoop):
        kwargs = {
            "server_settings": {
                'client_min_messages': 'notice',
                'max_parallel_workers': '24',
                'jit': 'off',
                'statement_timeout': '3600000'
            }
        }
        kwargs = {
            "server_settings": {
                "application_name": "DI:ExecuteSQL",
                "client_min_messages": "notice",
                "max_parallel_workers": "256",
                "jit": "off",
                "idle_in_transaction_session_timeout": DB_IDLE_TRANSACTION_TIMEOUT,
                "idle_session_timeout": DB_SESSION_TIMEOUT,
                "effective_cache_size": "2147483647",
                "tcp_keepalives_idle": DB_KEEPALIVE_IDLE,
                "statement_timeout": DB_STATEMENT_TIMEOUT
            },
        }
        return pg(dsn=asyncpg_url, loop=event_loop, timeout=360000, **kwargs)

    async def _execute(self, query, connection):
        try:
            async with await connection.connection() as conn:
                result, error = await conn.execute(
                    sentence=query
                )
                if error:
                    raise ComponentError(
                        f"Execute SQL error: {result!s} err: {error!s}"
                    )
                else:
                    return result
        except StatementError as err:
            raise StatementError(
                f"Statement error: {err}"
            ) from err
        except DataError as err:
            raise DataError(
                f"Data error: {err}"
            ) from err
        except ComponentError:
            raise
        except Exception as err:
            raise ComponentError(
                f"ExecuteSQL error: {err}"
            ) from err

    def execute_sql(self, query: str, event_loop: asyncio.AbstractEventLoop) -> str:
        asyncio.set_event_loop(event_loop)
        if self._debug:
            self._logger.verbose(
                f"::: Exec SQL: {query}"
            )
        connection = self.get_connection(event_loop)
        future = event_loop.create_task(
            self._execute(query, connection)
        )
        try:
            result = event_loop.run_until_complete(future)
            st = {
                "sql": query,
                "result": result
            }
            self.add_metric('EXECUTED', st)
            return result
        except Exception as err:
            self.add_metric('QUERY_ERROR', str(err))
            self._logger.error(
                f"{err}"
            )
        finally:
            connection = None

    async def run(self):
        """Run Raw SQL functionality."""
        try:
            ct = len(self.sql)
            if ct <= 0:
                ct = 1
            executor =  ThreadPoolExecutor(max_workers=ct)
            result = []
            for query in self.sql:
                try:
                    event_loop = asyncio.new_event_loop()
                    fn = partial(self.execute_sql, query, event_loop)
                    res = await self._loop.run_in_executor(executor, fn)
                    result.append(res)
                finally:
                    event_loop.close()
        except ComponentError:
            raise
        except Exception as err:
            raise ComponentError(
                f"{err}"
            ) from err
        # returning the previous data:
        if self.data is not None:
            self._result = self.data
        else:
            self._result = result
        return self._result
