
import re
import asyncio
import multiprocessing
from collections.abc import Callable
import gc
from io import BytesIO
import pandas as pd
import numpy as np
import json
import orjson
from asyncdb.exceptions import (
    ProviderError,
    StatementError,
    DataError,
    NoDataFound
)
import asyncpg
from asyncdb.drivers.pg import pg
from navconfig.conf import asyncpg_url
from navconfig.logging import logging
from navigator.conf import (
    DB_TIMEOUT,
    DB_STATEMENT_TIMEOUT,
    DB_SESSION_TIMEOUT,
    DB_IDLE_TRANSACTION_TIMEOUT,
    DB_KEEPALIVE_IDLE
)
# Dataintegration components:
from flowtask.utils import SafeDict
from flowtask.exceptions import (
    ComponentError
)
from .abstract import DtComponent


class CopyToPg(DtComponent):
    """
    CopyToPg.

    Overview

        This component allows copy data into a Postgres table,
        Copy into main postgres using copy_to_table functionality.
        TODO: Design an Upsert feature with Copy to Pg.

    .. table:: Properties
       :widths: auto


    +--------------+----------+-----------+-------------------------------------------------------+
    | Name         | Required | Summary                                                           |
    +--------------+----------+-----------+-------------------------------------------------------+
    | tablename    |   Yes    | Name of the table in                                              |
    |              |          | the database                                                      |
    +--------------+----------+-----------+-------------------------------------------------------+
    | schema       |   Yes    | Name of the schema                                                |
    |              |          | where is to the table                                             |
    +--------------+----------+-----------+-------------------------------------------------------+
    | truncate     |   Yes    | This option indicates if the component should empty the table     |
    |              |          | before coping the new data to the table. If set to true, the table|
    |              |          | will be truncated before saving the new data.                     |
    +--------------+----------+-----------+-------------------------------------------------------+
    | use_buffer   |   No     | When activated, this option allows optimizing the performance of  |
    |              |          | the task, when dealing with large volumes of data.                |
    |              |          | It works by sending us the information as the previously sent     |
    |              |          |  is being consumed.dicates if the component should empty the table|
    +--------------+----------+-----------+-------------------------------------------------------+

    """
    def __init__(
            self,
            loop: asyncio.AbstractEventLoop = None,
            job: Callable = None,
            stat: Callable = None,
            **kwargs
    ):
        self.pk = []
        self.truncate: bool = False
        self.data = None
        self._engine = None
        self.tablename: str = ''
        self.schema: str = ''
        self.use_chunks = False
        self.chunksize = None
        self._connection: Callable = None
        try:
            self.multi = bool(kwargs['multi'])
            del kwargs['multi']
        except KeyError:
            self.multi = False
        super(CopyToPg, self).__init__(
            loop=loop,
            job=job,
            stat=stat,
            **kwargs
        )

    async def start(self, **kwargs):
        """Obtain Pandas Dataframe."""
        if self.previous:
            self.data = self.input
        else:
            raise ComponentError(
                "Data Was Not Found"
            )
        for attr, value in self.__dict__.items():
            if isinstance(value, str):
                val = value.format_map(SafeDict(**self._variables))
                object.__setattr__(self, attr, val)
        if not self.schema:
            try:
                self.schema = self._program
            except (ValueError, AttributeError, TypeError) as ex:
                raise ComponentError(
                    "CopyToPg: Schema name not defined."
                ) from ex

    async def close(self):
        """Method."""
        try:
            await self._connection.close()
        except Exception as err:
            logging.error(err)

    async def paralelize_insert(self, columns, tuples):
        result = False
        try:
            result = await self._connection.copy_into_table(
                table=self.tablename,
                schema=self.schema,
                source=tuples,
                columns=columns
            )
            return result
        except StatementError as err:
            logging.exception(
                f"Statement Error: {err}",
                stack_info=True
            )
        except DataError as err:
            logging.exception(
                f"Data Error: {err}",
                stack_info=True
            )
        except Exception as err:
            logging.exception(
                f"Pg Error: {err}",
                stack_info=True
            )

    async def get_connection(self):
        try:
            kwargs = {
                "server_settings": {
                    "application_name": "CopyToPg",
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
            self._connection = pg(dsn=asyncpg_url, loop=self._loop, **kwargs)
            await self._connection.connection()
        except Exception as err:
            raise ProviderError(
                f'Error configuring pg Connection: {err!s}'
            ) from err
        return self._connection

    def extract_copied(self, result) -> int:
        try:
            return int(re.findall(r'\bCOPY\s(\d+)', result)[0])
        except Exception as err:
            logging.error(err)
            return None

    async def run(self):
        """Run Copy into table functionality."""
        self._result = None
        if self.data is None or self.data.empty:
            raise NoDataFound(
                "CopyToPg: Data was Not Found"
            )
        self._result = self.data
        columns = list(self.data.columns)
        self.add_metric('NUM_ROWS', self.data.shape[0])
        self.add_metric('NUM_COLUMNS', self.data.shape[1])
        if self._debug:
            print('Debugging: COPY TO PG ===')
            for column in columns:
                t = self.data[column].dtype
                print(column, '->', t, '->', self.data[column].iloc[0])
        # get connection
        self._connection = await self.get_connection()
        if self.truncate is True:
            if self._debug:
                logging.debug(f"Truncating table: {self.schema}.{self.tablename}")
            truncate = """
            SELECT pg_advisory_xact_lock(1);
            TRUNCATE {}.{};
            """
            truncate = truncate.format(self.schema, self.tablename)
            result, error = await self._connection.execute(truncate)
            if error is not None:
                raise ComponentError(
                    f"CopyToPg: Error truncating Table {self.schema}.{self.tablename}: {error}"
                )
            else:
                await self._connection.execute('SELECT pg_advisory_unlock_all();')
            logging.debug(f'TRUNCATE: {result}')
            await asyncio.sleep(5e-3)
        try:
            if isinstance(self.data, pd.DataFrame):
                # insert data directly into table
                columns = list(self.data.columns)
                if hasattr(self, 'use_chunks') and self.use_chunks is True:
                    logging.debug(':: Saving data using Chunks ::')
                    # TODO: paralelize CHUNKS
                    # calculate the chunk size as an integer
                    if not self.chunksize:
                        num_cores = multiprocessing.cpu_count()
                        chunk_size = int(self.data.shape[0]/num_cores) - 1
                    else:
                        chunk_size = self.chunksize
                    if chunk_size == 0:
                        raise ComponentError(
                            'CopyToPG: Wrong ChunkSize or Empty Dataframe'
                        )
                    chunks = (self.data.loc[self.data.index[i:i + chunk_size]]
                              for i in range(0, self.data.shape[0], chunk_size))
                    count = 0
                    numrows = 0
                    for chunk in chunks:
                        logging.debug(f'Iteration {count}')
                        s_buf = BytesIO()
                        chunk.to_csv(s_buf, index=None, header=None)
                        s_buf.seek(0)
                        try:
                            await self._connection.engine().set_type_codec(
                                "jsonb", encoder=orjson.dumps, decoder=orjson.loads, schema="pg_catalog"
                            )
                            await self._connection.engine().set_type_codec(
                                "json", encoder=orjson.dumps, decoder=orjson.loads, schema="pg_catalog"
                            )
                            result = await self._connection.engine().copy_to_table(
                                table_name=self.tablename,
                                schema_name=self.schema,
                                source=s_buf,
                                columns=columns,
                                format="csv"
                            )
                            rows = self.extract_copied(result)
                            numrows += rows
                            count += 1
                        except StatementError as err:
                            logging.error(f'Statement Error: {err}')
                            continue
                        except DataError as err:
                            logging.error(f'Data Error: {err}')
                            continue
                        await asyncio.sleep(5e-3)
                    self.add_metric('ROWS_SAVED', numrows)
                else:
                    try:
                        result = None
                        # insert data directly into table
                        if hasattr(self, "use_buffer"):
                            if hasattr(self, 'array_columns'):
                                for col in self.array_columns:
                                    # self.data[col].notna()
                                    self.data[col] = self.data[col].apply(lambda x: "{" + ",".join("'" + str(i) + "'" for i in x) + "}" if isinstance(x, (list, tuple)) and len(x) > 0 else np.nan)

                            s_buf = BytesIO()
                            self.data.to_csv(s_buf, index=None, header=None)
                            s_buf.seek(0)
                            if hasattr(self, "clean_df"):
                                del self.data
                                gc.collect()
                                self.data = pd.DataFrame()
                            await self._connection.engine().set_type_codec(
                                "json",
                                encoder=orjson.dumps, decoder=orjson.loads,
                                schema='pg_catalog'
                            )
                            await self._connection.engine().set_type_codec(
                                "jsonb",
                                encoder=orjson.dumps, decoder=orjson.loads,
                                schema="pg_catalog",
                                format="binary"
                            )
                            try:
                                result = await self._connection.engine().copy_to_table(
                                    table_name=self.tablename,
                                    schema_name=self.schema,
                                    source=s_buf,
                                    columns=columns,
                                    format="csv",
                                    timeout=360
                                )
                            except asyncpg.exceptions.DataError as e:
                                print(f"Error message: {e}")
                        else:
                            # can remove NAT from str fields:
                            u = self.data.select_dtypes(include=['string'])
                            if not u.empty:
                                self.data[u.columns] = u.astype(
                                    object).where(pd.notnull(u), None)
                            tuples = list(zip(*map(self.data.get, self.data)))
                            result = await self._connection.copy_into_table(
                                table=self.tablename,
                                schema=self.schema,
                                source=tuples,
                                columns=columns
                            )
                        self.add_metric('ROWS_SAVED', self.extract_copied(result))
                        if self._debug:
                            logging.debug(
                                f"Saving results into: {self.schema}.{self.tablename}"
                            )
                    except StatementError as err:
                        raise StatementError(
                            f"Statement error: {err}"
                        ) from err
                    except DataError as err:
                        raise ComponentError(
                            f"Data error: {err}"
                        ) from err
                    except Exception as err:
                        raise ComponentError(
                            f"{self.TaskName} Error: {err!s}"
                        ) from err
            else:
                tuples = [tuple(x.values()) for x in self.data]
                row = self.data[0]
                columns = list(row.keys())
                try:
                    #TODO: iterate the data into chunks (to avoid kill the process)
                    result = await self._connection.copy_into_table(
                        table=self.tablename,
                        schema=self.schema,
                        source=tuples,
                        columns=columns
                    )
                    self.add_metric('ROWS_SAVED', self.extract_copied(result))
                    logging.debug('CopyToPg: {result}')
                except StatementError as err:
                    raise StatementError(
                        f"Statement error: {err}"
                    ) from err
                except DataError as err:
                    raise ComponentError(
                        f"Data error: {err}"
                    ) from err
                except Exception as err:
                    raise ComponentError(
                        f"{self.TaskName} Error: {err!s}"
                    ) from err
            logging.debug(
                f"CopyToPg: Saving results into: {self.schema}.{self.tablename}"
            )
            # returning this
            # passing through
            return self._result
        except Exception as err:
            raise ComponentError(
                f"{self.TaskName} Error: {err!s}"
            ) from err
