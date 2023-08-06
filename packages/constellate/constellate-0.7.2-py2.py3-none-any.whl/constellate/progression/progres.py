from io import TextIOWrapper, BytesIO
from typing import Callable, TypeVar, Iterable

from tqdm.asyncio import tqdm as tqdm_asyncio


class _TextIOWrapperLogger(TextIOWrapper):
    def __init__(self, buffer: BytesIO, log: Callable = None, **kwargs):
        super().__init__(buffer, **kwargs)
        self._log = log

    def write(self, __s: str) -> int:
        total = len(__s)
        if total > 0 and __s != "\n" and __s != "\r\n":
            self._log(__s)
        return total


_T = TypeVar("_T")


class Progress:
    def __init__(self, log: Callable = None, **kwargs):
        self._log = log
        self._kwargs = kwargs

    def __call__(self, iterator: Iterable[_T] = None) -> tqdm_asyncio:
        def _discard_log(msg, *args, **kwargs):
            pass

        _log = self._log or _discard_log
        file = _TextIOWrapperLogger(
            buffer=BytesIO(), log=_log, write_through=True, errors="strict", newline=""
        )
        return tqdm_asyncio(iterator, file=file, **self._kwargs)
