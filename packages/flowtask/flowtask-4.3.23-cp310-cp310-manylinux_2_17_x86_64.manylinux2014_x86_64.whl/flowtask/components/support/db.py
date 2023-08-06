from typing import Optional
import asyncio
from abc import ABC
from asyncdb import AsyncDB
from flowtask.conf import default_dsn


class DBSupport(ABC):
    """
    Interface for adding AsyncbDB-based Database Support to Components.
    """
    _loop: asyncio.AbstractEventLoop

    def get_connection(
        self,
        event_loop: Optional[asyncio.AbstractEventLoop] = None,
        driver: str = 'pg',
        params: Optional[dict] = None,
        **kwargs
    ):
        # TODO: datasources and credentials
        if not kwargs and driver == 'pg':
            kwargs = {
                "server_settings": {
                    'client_min_messages': 'notice',
                    'max_parallel_workers': '24',
                    'jit': 'off',
                    'statement_timeout': '3600000'
                }
            }
        if not event_loop:
            event_loop = self._loop
        return AsyncDB(
            driver,
            dsn=default_dsn,
            loop=event_loop,
            timeout=360000,
            params=params,
            **kwargs
        )

    def db_connection(
            self,
            driver: str = 'pg',
            credentials: Optional[dict] = None,
            event_loop: Optional[asyncio.AbstractEventLoop] = None
        ):
        if not credentials:
            credentials = {
                "dsn": default_dsn
            }
        else:
            credentials = {
                "params": credentials
            }
        kwargs = {}
        if driver == 'pg':
            kwargs = {
                "server_settings": {
                    'client_min_messages': 'notice',
                    'max_parallel_workers': '24',
                    'jit': 'off',
                    'statement_timeout': '3600000'
                }
            }
        if not event_loop:
            event_loop = self._loop
        return AsyncDB(driver, loop=event_loop, timeout=360000, **credentials, **kwargs)
