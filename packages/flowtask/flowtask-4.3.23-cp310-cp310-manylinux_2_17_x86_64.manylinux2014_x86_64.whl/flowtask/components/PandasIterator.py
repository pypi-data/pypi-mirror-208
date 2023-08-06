import asyncio
from decimal import Decimal
from typing import Any
from collections.abc import Callable
import pandas
import numpy as np
from navconfig.logging import logging
from asyncdb.exceptions import NoDataFound, ProviderError
from flowtask.exceptions import (
    ComponentError,
    NotSupported,
    DataNotFound
)
from .IteratorBase import IteratorBase


class PandasIterator(IteratorBase):
    """
    PandasIterator.

    Overview

        This component convert to pandas dataframe in an Iterator

    .. table:: Properties
       :widths: auto


    +--------------+----------+-----------+-------------------------------------------------------+
    | Name         | Required | Summary                                                           |
    +--------------+----------+-----------+-------------------------------------------------------+
    |  columns     |   Yes    | Name of the column that we are going to extract going to extract  |
    +--------------+----------+-----------+-------------------------------------------------------+
    |  vars        |   Yes    | This attribute organizes name of the columns organized by id      |
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
        self.pk = []
        self.data = None
        self._iterator: Any = None
        self._variables = {}
        self.vars = {}
        self._columns = []
        self._result = None
        super(PandasIterator, self).__init__(
            loop=loop,
            job=job,
            stat=stat,
            **kwargs
        )

    async def start(self, **kwargs):
        """Obtain Pandas Dataframe."""
        if self.previous:
            self.data = self.input
            if isinstance(self.data, pandas.core.frame.DataFrame):
                if not hasattr(self, 'columns'):
                    # iterate over the total columns of dataframe
                    self._columns = self.data.columns
                else:
                    self._columns = self.columns
                self._iterator = self.data.iterrows()
            else:
                raise ComponentError(
                    'PandasIterator: Invalid type of Data input (requires a Pandas Dataframe)'
                )
        return True

    async def close(self, job=None):
        close = getattr(job, 'close', None)
        if job:
            if asyncio.iscoroutinefunction(close):
                await job.close()
            else:
                job.close()

    def createJob(self, target, params, row):
        """Create the Job Component."""
        self._result = self.data
        dt = {}
        for column in self._columns:
            value = row[column]
            if isinstance(value, (int, np.int64, np.integer)):
                value = int(value)
            elif isinstance(value, (float, Decimal)):
                value = float(value)
            self.setVar(column, value)
            params[column] = value
            dt[column] = value
        args = params['params']
        for name, value in self.vars.items():
            if isinstance(value, list):
                # TODO: logic to use functions with dataframes
            #     # need to calculate the value
                if name in args:
                    # replace value with args:
                    value = args[name]
                elif name in dt:
                    value = dt[name]
            else:
                if '{' in str(value):
                    try:
                        value = value.format(**args)
                    except KeyError:
                        value = value.format(**dt)
            params[name] = value
            self.setVar(name, value)
        return self.get_job(target, **params)

    async def run(self):
        """Async Run Method."""
        # iterate over next task
        step, target, params = self.get_step()
        step_name = step.name
        i = 0
        for _, row in self._iterator:
            i += 1
            # logging.debug(f'ITER: index:{index} row: {row}')
            # iterate over every row
            # get I got all values, create a job:
            job = self.createJob(target, params, row)
            if job:
                try:
                    self._result = await self.async_job(job, step_name)
                except (NoDataFound, DataNotFound) as err:
                    # its a data component a no data was found
                    logging.debug(
                        f'Data not Found for Task {step_name}, got: {err}'
                    )
                    continue
                except (ProviderError, ComponentError) as err:
                    raise ComponentError(
                        f"Error on {step_name}, error: {err}"
                    ) from err
                except NotSupported as err:
                    raise NotSupported(
                        f"Not Supported: {err}") from err
                except Exception as err:
                    raise ComponentError(
                        f"Component Error {step_name}, error: {err}"
                    ) from err
                finally:
                    await self.close(job)
        self.add_metric('ITERATIONS', i)
        # returning last value generated by iteration
        return self._result
