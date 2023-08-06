import asyncio
from asyncio import futures, coroutines, ensure_future, Queue
from typing import Iterator, Any, AsyncGenerator

from bidict import bidict


async def as_completed(
    fs: Iterator[Any], *, timeout=None, return_exception: bool = False
) -> AsyncGenerator[Any, None]:
    """Return an async generator whose values are coroutines.

    When waiting for the yielded coroutines you'll get the results (or
    exceptions!) of the original Futures (or coroutines), in the order
    in which and as soon as they complete.

    This differs from PEP 3148; the proper way to use this is:

        async for f in as_completed(fs):
            result = f
            # Use result.

    If a timeout is specified, the 'await' will raise
    TimeoutError when the timeout occurs before all Futures are done.

    Note: The futures 'f' are not necessarily members of fs.
    """
    if futures.isfuture(fs) or coroutines.iscoroutine(fs):
        raise TypeError(f"expect a list of futures, not {type(fs).__name__}")

    SENTINEL = object()
    done = Queue()

    _priority = -1
    todo = {}
    for f in fs:
        _priority += 1
        todo[_priority] = ensure_future(f)

    todo = bidict(todo)

    ready = {}
    timeout_handle = None

    def _on_timeout():
        # Nothing left to do since there is no time left to do anything
        for priority, f in list(todo.items()):
            f.remove_done_callback(_on_completion)
            done.put_nowait((None, None))  # Queue a dummy value for _wait_for_one().
            todo.remove(priority)

    def _on_completion(f):
        if not todo:
            return  # _on_timeout() was here first.
        priority = todo.inverse.pop(f, None)
        done.put_nowait((priority, f))
        if not todo and timeout_handle is not None:
            timeout_handle.cancel()

    async def _wait_for_one(expected_priority):
        r = ready.pop(expected_priority, SENTINEL)
        if r is not SENTINEL:
            return r

        priority, f = await done.get()
        if priority is None and f is None:
            # Dummy value from _on_timeout().
            raise asyncio.exceptions.TimeoutError

        try:
            r = f.result()  # May raise f.exception().
            ready[priority] = r

            r = ready.pop(expected_priority, SENTINEL)
            return r
        except BaseException as e:
            if return_exception:
                ready[priority] = e
                return e
            else:
                # Propagate
                raise e

    for priority, f in list(todo.items()):
        f.add_done_callback(_on_completion)
    if todo and timeout is not None:
        timeout_handle = asyncio.call_later(timeout, _on_timeout)

    priority = -1
    exhausted = False
    while len(list(todo.keys())) > 0:
        priority += 1
        result = await _wait_for_one(priority)
        if result is not SENTINEL:
            yield result
        else:
            priority -= 1
        await asyncio.sleep(0)
