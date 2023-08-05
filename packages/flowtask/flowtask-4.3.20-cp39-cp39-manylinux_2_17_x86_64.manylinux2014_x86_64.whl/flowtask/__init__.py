# -*- coding: utf-8 -*-
"""
Navigator Data-Integration.

Tool for execution of Tasks.
"""
import asyncio
import uvloop
from .version import (
    __title__, __description__, __version__, __author__, __author_email__
)

# install uvloop and set as default loop for asyncio.
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
uvloop.install()

def version():
    """version.
    Returns:
        str: current version of Navigator flowtask.
    """
    return __version__
