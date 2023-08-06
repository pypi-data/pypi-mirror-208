from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import contextmanager


@contextmanager
def new_threadpool(*args, wait=True, **kwds) -> ThreadPoolExecutor:
    resource = ThreadPoolExecutor(*args, **kwds)
    try:
        yield resource
    finally:
        resource.shutdown(wait=wait)


@contextmanager
def new_processpool(*args, wait=True, **kwds) -> ProcessPoolExecutor:
    resource = ProcessPoolExecutor(*args, **kwds)
    try:
        yield resource
    finally:
        resource.shutdown(wait=wait)
