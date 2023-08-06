# this is a wrapper for the `asyncio` module
# pyright: reportWildcardImportFromLibrary=false
# pylint: disable=wildcard-import,unused-wildcard-import

import asyncio
import contextvars
import functools
from asyncio import *
from typing import Any


# https://stackoverflow.com/a/69165563
# TODO: replace with asyncio.to_thread once Python gets updated to 3.9+
async def to_thread(func, /, *args: Any, **kwargs: Any):
    loop = asyncio.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)
