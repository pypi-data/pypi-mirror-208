import logging
import asyncio
from pathlib import Path, PurePath
from typing import Any
from collections.abc import Callable
from pprint import pprint
from aiofile import AIOFile
import urllib3
import pandas as pd
import numpy as np
from asyncdb.drivers.pg import pg
from asyncdb.exceptions import NoDataFound
from querysource.exceptions import DataNotFound as NoData
from querysource.queries.qs import QS
from querysource.types.validators import Entity
from flowtask.exceptions import (
    ComponentError,
    DataNotFound,
    NotSupported,
    FileError
)
from flowtask.utils import cPrint, is_empty, SafeDict
from settings.settings import TASK_PATH, asyncpg_url
from .abstract import DtComponent

urllib3.disable_warnings()
logging.getLogger("urllib3").setLevel(logging.WARNING)


class QueryToPandas(DtComponent):
    """QueryToPandas.

    Overview

        This component allows executing queries to a database

    .. table:: Properties
       :widths: auto

    +--------------+----------+-----------+-------------------------------------------------------+
    | Name         | Required | Summary                                                           |
    +--------------+----------+-----------+-------------------------------------------------------+
    | query        |   Yes    | Represents an SQL query                                           |
    +--------------+----------+-----------+-------------------------------------------------------+
    | query_slug   |   Yes    | Named queries that are saved in Navigator (QuerySource)           |
    +--------------+----------+-----------+-------------------------------------------------------+
    | as_dict      |   Yes    | True | False. if true, it returns the data in JSON format         |
    |              |          | instead of a dataframe                                            |
    +--------------+----------+-----------+-------------------------------------------------------+
    | raw_result   |   Yes    | Returns the data in the NATIVE FORMAT of the database for         |
    |              |          | example ( pg RECORDSET)                                           |
    +--------------+----------+-----------+-------------------------------------------------------+
    | file_sql     |   Yes    | SQL comes from a sql file                                         |
    +--------------+----------+-----------+-------------------------------------------------------+
    | use_template |   Yes    | The component is passed to the SQL file through a  template       |
    |              |          | replacement system                                                |
    +--------------+----------+-----------+-------------------------------------------------------+
    | infer_types  |   Yes    | Type inference, give the component the power to decide the data   |
    |              |          | types of each column                                              |
    +--------------+----------+-----------+-------------------------------------------------------+
    | drop_empty   |   Yes    | False | True  delete (drop) any column that is empty              |
    +--------------+----------+-----------+-------------------------------------------------------+
    | dropna       |   Yes    | False | True  delete all NA (Not a Number)                        |
    +--------------+----------+-----------+-------------------------------------------------------+
    | fillna       |   Yes    | False | True  fills with an EMPTY SPACE all the NAs of the        |
    |              |          | dataframe                                                         |
    +--------------+----------+-----------+-------------------------------------------------------+
    | clean_strings|   Yes    | Fills with an empty space the NA,but ONLY of the fields of        |
    |              |          | type string                                                       |
    +--------------+----------+-----------+-------------------------------------------------------+
    | clean_dates  |   Yes    | Declares NONE any date field that has a NAT (Not a Time)          |
    +--------------+----------+-----------+-------------------------------------------------------+
    | conditions   |   Yes    | This attribute allows me to apply conditions to filter the data   |
    +--------------+----------+-----------+-------------------------------------------------------+
    | dwh          |    Yes   |                                                                   |
    +--------------+----------+-----------+-------------------------------------------------------+
    | formit       |   Yes    | Form id                                                           |
    +--------------+----------+-----------+-------------------------------------------------------+
    | orgid        |   Yes    | Organization id                                                   |
    +--------------+----------+-----------+-------------------------------------------------------+
    | refresh      |   Yes    | Refreshes the data in the QueryToPandas                           |
    +--------------+----------+-----------+-------------------------------------------------------+


    """
    def __init__(
            self,
            loop: asyncio.AbstractEventLoop = None,
            job: Callable = None,
            stat: Callable = None,
            **kwargs
    ):
        """Init Method."""
        self.data = None
        self.datasource = 'db'
        self.infer_types: bool = False
        self.to_string: bool = True
        self._query: dict = {}
        self.as_dict: bool = False
        self.as_objects: bool = False
        self._dtypes: dict = {}
        try:
            self.use_template: bool = bool(kwargs['use_template'])
            del kwargs['use_template']
        except KeyError:
            self.use_template: bool = False
        super(QueryToPandas, self).__init__(
            loop=loop, job=job, stat=stat, **kwargs
        )

    def set_datatypes(self):
        if hasattr(self, 'datatypes'):
            dtypes = {}
            for field, dtype in self.datatypes.items():
                if dtype == 'uint8':
                    dtypes[field] = np.uint8
                elif dtype == 'uint16':
                    dtypes[field] = np.uint16
                elif dtype == 'uint32':
                    dtypes[field] = np.uint32
                elif dtype == 'int8':
                    dtypes[field] = np.int8
                elif dtype == 'int16':
                    dtypes[field] = np.int16
                elif dtype == 'int32':
                    dtypes[field] = np.int32
                elif dtype == 'float':
                    dtypes[field] = float
                elif dtype == 'float32':
                    dtypes[field] = float
                elif dtype in ('string', 'varchar', 'str'):
                    dtypes[field] = str
                else:
                    # invalid datatype
                    self._logger.warning(
                        f'Invalid DataType value: {field} for field {dtype}'
                    )
                    continue
            if dtypes:
                self._dtypes['dtype'] = dtypes

    async def open_sqlfile(self, file: PurePath, **kwargs) -> str:
        if file.exists() and file.is_file():
            content = None
            # open SQL File:
            async with AIOFile(file, 'r+') as afp:
                content = await afp.read()
                # check if we need to replace masks
            if hasattr(self, 'masks'):
                content = self.mask_replacement(
                    content
                )
            if self.use_template is True:
                content = self._templateparser.from_string(
                    content, kwargs
                )
            return content
        else:
            raise FileError(
                f'{self.__name__}: Missing SQL File: {file}'
            )

    def get_connection(self, event_loop: asyncio.AbstractEventLoop):
        # TODO: datasources and credentials
        kwargs = {
            "server_settings": {
                'client_min_messages': 'notice',
                'max_parallel_workers': '24',
                'jit': 'off',
                'statement_timeout': '3600000'
            }
        }
        return pg(dsn=asyncpg_url, loop=event_loop, timeout=360000, **kwargs)

    async def start(self, **kwargs):
        await super(QueryToPandas, self).start(**kwargs)
        # check if sql comes from a filename:
        if hasattr(self, 'file_sql') or hasattr(self, 'query_file'): # based on a list/dict of queries
            if hasattr(self, 'file_sql'):
                query = self.file_sql
            else:
                query = self.query_file
            if isinstance(query, PurePath):
                self._query = []
                if query.exists() and query.is_file():
                    sql = await self.open_sqlfile(query)
                    self._query.append(sql)
            elif isinstance(query, str):
                self._query = []
                try:
                    file_path = Path(TASK_PATH).joinpath(
                        self._program, 'sql', query
                    )
                    if file_path.exists() and file_path.is_file():
                        sql = await self.open_sqlfile(file_path)
                        self._query.append(sql)
                except Exception as ex:
                    raise FileError(
                        f'File SQL doesn\'t exists: {query!s}: {ex}'
                    ) from ex
            elif isinstance(query, list): # list of queries
                self._query = []
                for file_sql in query:
                    file_path = Path(TASK_PATH).joinpath(
                        self._program, 'sql', file_sql
                    )
                    if file_path.exists() and file_path.is_file():
                        sql = await self.open_sqlfile(file_path)
                        self._query.append(sql)
            elif isinstance(query, dict): # named queries
                self._query = {}
                for key, file_sql in query.items():
                    file_path = Path(TASK_PATH).joinpath(
                        self._program, 'sql', file_sql
                    )
                    if file_path.exists() and file_path.is_file():
                        sql = await self.open_sqlfile(file_path)
                        self._query[key] = sql
        elif hasattr(self, 'query_slug'):
            if isinstance(self.query_slug, str): # pylint: disable=E0203
                self.query_slug = self.mask_replacement(
                    self.query_slug
                )
                self._query[self.query_slug] = self.query_slug
            elif isinstance(self.query_slug, list):
                for slug in self.query_slug:
                    self._query[slug] = slug
            elif isinstance(self.query_slug, dict):
                # iterate over all conditions and search in masks:
                for key, data in self.query_slug.items():
                    slug = data['slug']
                    for mask, replace in self._mask.items():
                        if mask in data['conditions']:
                            self.query_slug[key]['conditions'][mask] = replace
                    self._query[key] = slug
        elif hasattr(self, 'query'):
            if isinstance(self.query, str): # pylint: disable=E0203
                self._query = []
                if hasattr(self, 'masks'):
                    self.query = self.mask_replacement(
                        self.query
                    )
                try:
                    self.query = self.query.format(**self._variables)
                except Exception as err:
                    print('Error replacing Vars in Query: ', err)
                self._query.append(self.query)
            elif isinstance(self.query, dict): # named queries
                self._query = {}
                for key, query in self.query.items():
                    query = self.mask_replacement(query)
                    try:
                        query = query.format(**self._variables)
                    except Exception:
                        pass
                    self._query[key] = query
            elif isinstance(self.query, list): # need to be concatenated
                self._query = []
                for query in self.query:
                    query = self.mask_replacement(query)
                    try:
                        for val in self._variables:
                            if isinstance(self._variables[val], list):
                                result = ', '.join(self._variables[val])
                            else:
                                result = ', '.join("'{}'".format(v) for v in self._variables[val])
                        query = query.format(**self._variables)
                    except Exception:
                        pass
                    self._query.append(query)
        if hasattr(self, 'conditions'):
            self.set_conditions('conditions')
            cPrint('NEW CONDITIONS ARE> ', level='WARN')
            pprint(self.conditions)

        # Replace variables
        if isinstance(self._query, list):
            queries = []
            for query in self._query:
                values = {}
                for key,val in self._variables.items():
                    if isinstance(val, list):
                        value = ', '.join("'{}'".format(Entity.quoteString(v)) for v in val)
                    else:
                        value = val
                    query = query.replace('{{{}}}'.format(str(key)), str(value))
                    values[key] = value
                # using safeDict
                query.format_map(SafeDict(**values))
                queries.append(query)
            self._query = queries
        return True

    async def close(self):
        """Method."""

    async def run(self):
        # TODO: support for datasources
        # TODO: using maps to transform data types
        if not self._query:
            raise ComponentError(
                'QueryToPandas: Empty Query/Slug or File'
            )
        if hasattr(self, 'query') or hasattr(self, 'file_sql'):
            try:
                connection = self.get_connection(event_loop=self._loop)
            except Exception as err:
                logging.exception(err, stack_info=True)
                raise
            if isinstance(self._query, list): # list of queries
                results = []
                async with await connection.connection() as conn:
                    for query in self._query:
                        try:
                            res, error = await conn.query(query)
                            if error:
                                raise NoDataFound(error)
                            result = [dict(row) for row in res]
                        except NoDataFound:
                            result = []
                        except Exception as err:
                            logging.error(err)
                            raise
                        l = len(result)
                        st = {
                            # "query": query,
                            "result": l
                        }
                        self.add_metric('Query', st)
                        if l == 1 and self.as_dict is True:
                            # saving only one row
                            result = dict(result[0])
                            results.append(result)
                        else:
                            results.extend(result)
                if hasattr(self, 'raw_result'):
                    self._result = results
                    self._variables[f'{self.TaskName}_NUMROWS'] = len(results)
                else:
                    self._result = await self.get_dataframe(
                        results,
                        infer_types=True
                    )
                    numrows = len(self._result.index)
                    self._variables[f'{self.TaskName}_NUMROWS'] = numrows
            elif isinstance(self._query, dict): # Named queries
                self._result = {}
                results = []
                async with await connection.connection() as conn:
                    for key, query in self._query.items():
                        try:
                            res, error = await conn.query(query)
                            if error:
                                raise NoDataFound(error)
                            result = [dict(row) for row in res]
                        except NoDataFound:
                            result = []
                        except Exception as err:
                            logging.error(err)
                            raise
                        l = len(result)
                        st = {
                            "query": key,
                            "result": l
                        }
                        self.add_metric('Query', st)
                        if l == 1:
                            # saving only one row
                            result = dict(result[0])
                        if hasattr(self, 'raw_result'):
                            self._result[key] = result
                            self._variables[f'{self.TaskName}_{key}_NUMROWS'] = len(result)
                        else:
                            df = await self.get_dataframe(
                                result,
                                infer_types=True
                            )
                            self._result[key] = df
                            self._variables[f'{self.TaskName}_{key}_NUMROWS'] = len(df.index)
            else:
                raise NotSupported(
                    f"{self.__name__}: Incompatible Query Method."
                )
        elif hasattr(self, 'query_slug'):
            # TODO: assign the datasource to QuerySource connection
            if isinstance(self.query_slug, dict):
                # return a list of queries
                self._result = {}
                for key, data in self.query_slug.items():
                    slug = data['slug']
                    conditions = data['conditions']
                    try:
                        result = await self.get_query(slug, conditions)
                        l = len(result)
                        st = {
                            "query": key,
                            "result": l
                        }
                        # self.add_metric(f'Query: {key}', st)
                        if l == 1 and self.as_dict is True:
                            # saving only one row
                            result = dict(result[0])
                    except (DataNotFound, NoDataFound) as ex:
                        raise DataNotFound(str(ex)) from ex
                    if hasattr(self, 'raw_result'):
                        self._result[key] = result
                        self._variables[f'{self.TaskName}_{key}_NUMROWS'] = len(result)
                    else:
                        df = await self.get_dataframe(
                            result,
                            infer_types=True
                        )
                        self._result[key] = df
                        self._variables[f'{self.TaskName}_{key}_NUMROWS'] = len(df.index)
            else:
                results = []
                for key, slug in self._query.items():
                    conditions = {}
                    if hasattr(self, 'conditions'):
                        conditions = self.conditions
                    try:
                        result = await self.get_query(slug, conditions)
                        l = len(result)
                        st = {
                            "query": key,
                            "result": l
                        }
                        # self.add_metric(f'Query: {key}', st)
                        if l == 1 and self.as_dict is True:
                            # saving only one row
                            result = dict(result[0])
                    except (DataNotFound, NoDataFound):
                        result = {}
                    except Exception as err:
                        logging.exception(err, stack_info=False)
                        raise
                    results.extend(result)
                if hasattr(self, 'raw_result'):
                    self._result = results
                    print('RESULT: ', self._result)
                    self._variables[f'{self.TaskName}_NUMROWS'] = len(results)
                else:
                    self._result = await self.get_dataframe(
                        results,
                        infer_types=True
                    )
                    numrows = len(self._result.index)
                    self._variables[f'{self.TaskName}_NUMROWS'] = numrows
        else:
            raise NotSupported(
                f"{self.__name__}: Method not allowed"
            )
        if is_empty(self._result):
            raise DataNotFound(
                f"{self.__name__}: Data Not Found"
            )
        else:
            ### making traspose of data:
            if hasattr(self, 'transpose'):
                # transpose rows to columns:
                # self._result = self._result.transpose()
                self._result = pd.melt(self._result, id_vars=self.transpose['columns'])
                if 'variable' in self.transpose:
                    # rename variable to a new name:
                    self._result.rename(columns = {'variable': self.transpose['variable']}, inplace = True)
                if 'value' in self.transpose:
                    self._result.rename(columns = {'value': self.transpose['value']}, inplace = True)
            if self._debug is True:
                print('== DATA PREVIEW ==')
                print(self._result)
                print()
            return self._result

    async def get_query(self, slug, conditions: dict = None):
        result: Any = []
        if not conditions:
            conditions = self.conditions
        try:
            qry = QS(
                slug=slug,
                conditions=conditions,
                loop=self._loop,
                lazy=True
            )
            await qry.build_provider()
        except (NoData, NoDataFound) as err:
            raise DataNotFound(
                str(err)
            ) from err
        except Exception as err:
            raise Exception(f"{err}") from err
        try:
            res, error = await qry.query()
            if not res:
                raise DataNotFound(
                    f'{slug}: Data Not Found'
                )
            if error:
                if isinstance(error, BaseException):
                    raise error
                else:
                    raise ComponentError(
                        f"Error on Query: {err}"
                    )
            result = result + [dict(row) for row in res]
            return result
        except (NoData, DataNotFound, NoDataFound) as err:
            raise DataNotFound(
                str(err)
            ) from err
        except Exception as err:
            raise ComponentError(
                f"Error on Query: {err}"
            ) from err
        finally:
            try:
                await qry.close()
            except Exception as ex: # pylint: disable=W0703
                self._logger.warning(ex)
            del qry

    async def get_dataframe(self, result, infer_types: bool = False):
        self.set_datatypes()
        print(self._dtypes)
        try:
            if self.as_objects is True:
                df = pd.DataFrame(
                    result,
                    dtype=object
                )
            else:
                df = pd.DataFrame(
                    result,
                    **self._dtypes
                )
        except Exception as err:
            logging.exception(err, stack_info=True)
        # Attempt to infer better dtypes for object columns.
        if hasattr(self, "infer_types") or infer_types is True:
            df.infer_objects()
            df = df.convert_dtypes(
                convert_string=self.to_string
            )
        if self._debug is True:
            cPrint('Data Types:')
            print(df.dtypes)
        if hasattr(self, "drop_empty"):
            df.dropna(axis=1, how='all', inplace=True)
            df.dropna(axis=0, how='all', inplace=True)
        if hasattr(self, 'dropna'):
            df.dropna(subset=self.dropna, how='all', inplace=True)
        if hasattr(self, 'clean_strings') and getattr(self, 'clean_strings', False) is True:
            u = df.select_dtypes(include=['object', 'string'])
            df[u.columns] = u.fillna('')
        return df
