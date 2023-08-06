"""
    QuerySource.
    QuerySource is a new kind of component supporting the new sources for
    QuerySource and making transformations of data, returning a transformed Pandas DataFrame.
"""
import logging
import asyncio
import importlib
from collections.abc import Callable
import pandas as pd
from querysource.exceptions import DataNotFound as DNF
from asyncdb.exceptions import NoDataFound
from flowtask.exceptions import (
    ComponentError,
    DataNotFound
)
from .abstract import DtComponent

class QSBase(DtComponent):
    """
    QSBase.

    Overview

            Helper to build components extend from QuerySource
    """
    type: str = 'None'
    _driver: str = 'QSBase'

    def __init__(
            self,
            loop: asyncio.AbstractEventLoop = None,
            job: Callable = None,
            stat: Callable = None,
            **kwargs
    ):
        """Init Method."""
        self._qs: Callable = None
        self._kwargs: dict = {}
        self.to_string: bool = True
        if 'type' in kwargs:
            self.type = kwargs['type']
            del kwargs['type']
        super(QSBase, self).__init__(
            loop=loop,
            job=job,
            stat=stat,
            **kwargs
        )

    async def start(self, **kwargs):
        if self.previous:
            self.data = self.input
        params = {
            "type": self.type
        }
        if hasattr(self, 'masks'):
            for key, val in self._attrs.items():
                if key in self._variables:
                    self._attrs[key] = self._variables[key]
                else:
                    self._attrs[key] = self.mask_replacement(val)
        if hasattr(self, 'pattern'):
            self.set_attributes('pattern')
        if self._attrs:
            params = {**params, **self._attrs}
        self._kwargs = params
        fns = f'querysource.providers.sources.{self._driver}'
        self.add_metric('Driver', {"driver": self._driver, "model": str(self.__class__.__name__)})
        # self.add_metric('Parameters', params)
        self._qs = None
        try:
            module = importlib.import_module(fns, package=self._driver)
            cls = getattr(module, self._driver)
            self._qs = cls(**params)
        except ModuleNotFoundError as err:
            raise Exception(
                f'Error importing {self._driver} module, error: {str(err)}'
            ) from err
        except Exception as err:
            raise Exception(
                f'Error: Unknown Error on {self._driver} module, error: {str(err)}'
            ) from err

    def create_dataframe(self, result):
        if not result:
            self._variables['_numRows_'] = 0
            self._variables[f'{self.TaskName}_NUMROWS'] = 0
            raise NoDataFound(
                "Data Not Found"
            )
        try:
            df = pd.DataFrame(result)
            # Attempt to infer better dtypes for object columns.
            df.infer_objects()
            if hasattr(self, "infer_types"):
                df = df.convert_dtypes(
                    convert_string=self.to_string
                )
            if hasattr(self, "drop_empty"):
                df.dropna(axis=1, how='all', inplace=True)
                df.dropna(axis=0, how='all', inplace=True)
            if hasattr(self, 'dropna'):
                df.dropna(subset=self.dropna, how='all', inplace=True)
            if self._debug:
                print(df)
                print('::: Printing Column Information === ')
                columns = list(df.columns)
                for column in columns:
                    t = df[column].dtype
                    print(column, '->', t, '->', df[column].iloc[0])
            self._variables['_numRows_'] = len(df.index)
            self._variables[f'{self.TaskName}_NUMROWS'] = len(df.index)
            return df
        except Exception as err:
            logging.error(f'{self._driver}: Error Creating Dataframe {err!s}')

    async def run(self):
        if hasattr(self, self.type):
            fn = getattr(self, self.type)
        elif hasattr(self._qs, self.type):
            fn = getattr(self._qs, self.type)
        else:
            fn = getattr(self._qs, 'query')
        if callable(fn):
            result = await fn()
            try:
                if isinstance(result, dict):
                    self._result = {}
                    # is a list of results, several dataframes at once
                    for key, res in result.items():
                        df = self.create_dataframe(res)
                        self._result[key] = df
                else:
                    df = self.create_dataframe(result)
                    if df is None or df.empty:
                        self._result = pd.DataFrame([])
                    self._result = df
                return True
            except (NoDataFound, DNF) as err:
                raise DataNotFound(
                    f'QS Data not Found: {err}'
                ) from err
            except Exception as err:
                logging.exception(err)
                raise ComponentError(err) from err
        else:
            raise ComponentError(
                f'{self._driver}: Cannot run Method {fn!s}'
            )

    async def close(self):
        """Closing QS Object."""
