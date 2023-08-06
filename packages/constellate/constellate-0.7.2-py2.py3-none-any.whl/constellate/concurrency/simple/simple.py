import asyncio
import concurrent.futures
from typing import Callable, Any, Union

from typing_extensions import TypeAlias

import pebble.pool
from decorator import decorator, decorate

_DEFAULT_PEBBLE_THREADPOOL = pebble.ThreadPool()
_DEFAULT_PEBBLE_PROCESSPOOL = pebble.ProcessPool()

SyncFunction: TypeAlias = Callable[[], Any]
SyncFunctionWrapper: TypeAlias = Callable[[], asyncio.Future]


@decorator
async def thread(
    fn: SyncFunction, pool: Union[pebble.ThreadPool] = None, *fn_args, **fn_kwargs
) -> asyncio.Future:
    """
    A decorator to run a function in a separate thread within a pool.
    Useful to any IO operations (network request, prints, etc...)
    and want to do something else while waiting for it to finish.
    :param pool: The pool to run the function on
    """
    pool = pool or _DEFAULT_PEBBLE_THREADPOOL
    if isinstance(pool, pebble.ThreadPool):
        future: concurrent.futures.Future = pool.schedule(fn, fn_args, fn_kwargs)
        # Asyncio future is awaitable in the current loop by default
        # src: https://stackoverflow.com/a/54105121/219728
        return await asyncio.wrap_future(future)

    raise NotImplemented()


#
# NOTE: @decorator hides the function being decorated with a closure. As such
#       this is incompatible with pickle / multiprocessing code.
#       Use the decorator process function below (see doc for usage)
#
# Context:
#  - https://pythonicthoughtssnippets.github.io/2020/08/09/PTS13-rethinking-python-decorators.html
#  - http://gael-varoquaux.info/programming/decoration-in-python-done-right-decorating-and-pickling.html
# @decorator
# async def process(fn: SyncFunction,
#                  pool: Union[pebble.ProcessPool] = None,
#                  *fn_args,
#                  **fn_kwargs) -> asyncio.Future:
#    """
#    A decorator to run a function in a separate process within a pool.
#    Useful to any IO operations (network request, prints, etc...)
#    and want to do something else while waiting for it to finish.
#    :param pool: The pool to run the function on
#    """
#    if isinstance(pool, pebble.ProcessPool):
#        pool = pool or _DEFAULT_PEBBLE_PROCESSPOOL
#        future: concurrent.futures.Future = pool.schedule(
#            fn, fn_args, fn_kwargs)
#        # Asyncio future is awaitable in the current loop by default
#        # src: https://stackoverflow.com/a/54105121/219728
#        return await asyncio.wrap_future(future)
#
#    raise NotImplemented()


async def process(
    fn: SyncFunction,
    pool: Union[pebble.ProcessPool] = None,
    future: bool = False,
    *fn_args,
    **fn_kwargs
) -> Union[asyncio.Future, Any]:
    """
    A decorator to run a function in a separate process within a pool.
    Useful to any IO operations (network request, prints, etc...)
    and want to do something else while waiting for it to finish.
    :param pool: The pool to run the function on
    :returns A future to hold teh result or the result itself (if future=False)
    ----
    Usage:
    async def my_func(a:str, b:str):
        return f"{a}+{b}"

    compute_long_operation = functools.partial(process, my_func, pool=A_PEBBLE_PROCESS_POOL, future=False)
    assert "foo+bar" == await compute_long_operation("foo", "bar")

    compute_long_operation = functools.partial(process, my_func, pool=A_PEBBLE_PROCESS_POOL, future=True)
    future = await compute_long_operation("foo", "bar")
    assert "foo+bar" == await future
    """

    f = await _process(fn=fn, pool=pool, *fn_args, **fn_kwargs)
    return f if future else await f


async def _process(
    fn: SyncFunction, pool: Union[pebble.ProcessPool] = None, *fn_args, **fn_kwargs
) -> asyncio.Future:
    pool = pool or _DEFAULT_PEBBLE_PROCESSPOOL
    if isinstance(pool, pebble.ProcessPool):
        future: concurrent.futures.Future = pool.schedule(fn, fn_args, fn_kwargs)
        # Asyncio future is awaitable in the current loop by default
        # src: https://stackoverflow.com/a/54105121/219728
        return asyncio.wrap_future(future)

    raise NotImplemented()
