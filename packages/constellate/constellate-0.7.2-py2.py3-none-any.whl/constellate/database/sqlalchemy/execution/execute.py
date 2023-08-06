import asyncio
from typing import Callable, Optional, List, Union, AsyncGenerator, Iterable, TypeVar

from aioitertools import chain
from decorator import decorator
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult
from sqlalchemy.sql import Select
import sqlalchemy.ext.asyncio.result
import sqlalchemy.ext.asyncio.session
import sqlalchemy.sql.selectable

X = TypeVar("X")


async def _execute_select(
    session: AsyncSession = None,
    execute: bool = True,
    stmt: Select = None,
    result_scalars: bool = None,
    result_scalar: bool = None,
    result_one_or_none: bool = None,
    result_one: bool = None,
    result_all: bool = None,
    result_stream: bool = None,
    result_stream_max_row_buffer: int = None,
    return_result_as_sqlalchemy_native: bool = None,
    return_result_as_iterable: bool = None,
    return_result_as_async_generator: bool = None,
    return_result_discard: bool = None,
) -> Union[X, Optional[X], Iterable[X], AsyncGenerator[X, None]]:
    if stmt is None:
        raise NotImplementedError()

    if not execute:
        return stmt

    if result_stream:
        # src:
        # https://docs.sqlalchemy.org/en/14/core/connections.html#using-server-side-cursors-a-k-a-stream-results
        stmt = stmt.execution_options(stream_results=True)

    result = await session.execute(stmt)

    if result_scalars is True:
        result = result.scalars()
    elif result_scalar is True:
        result = result.scalar()

    if result_one_or_none is True:
        result = result.one_or_none()
    elif result_one is True:
        result = result.one()
    elif result_all is True:
        result = result.all()

    if return_result_as_sqlalchemy_native:
        if result_stream:
            # result's type: iter[list[X]]
            result = (
                result.partitions(result_stream_max_row_buffer)
                if result_stream_max_row_buffer is not None
                else result
            )
            # result's type: iter[X]
            # result = chain.from_iterable(result)

        return await __execute_select_return_sqlalchemy_native(result=result)
    if return_result_as_iterable:
        if result_stream:
            # result's type: iter[list[X]]
            result = (
                result.partitions(result_stream_max_row_buffer)
                if result_stream_max_row_buffer is not None
                else result
            )
            # result's type: iter[X]
            # result = chain.from_iterable(result)

        return await __execute_select_return_iterable(result=result)
    elif return_result_as_async_generator:
        if result_stream:
            # result's type: iter[list[X]]
            result = (
                result.partitions(result_stream_max_row_buffer)
                if result_stream_max_row_buffer is not None
                else result
            )
            # result's type: iter[X]
            result = chain.from_iterable(result)
            # async generator
            return result

        # coroutine
        result = __execute_select_return_async_generator(result=result)
        # async generator
        return result
    elif return_result_discard:
        # 'Discard any rows left to fetch
        result.close()
        return None
    else:
        raise NotImplementedError()


async def __execute_select_return_sqlalchemy_native(
    result: AsyncResult = None,
) -> Union[X, Optional[X], List[X]]:
    return result


async def __execute_select_return_iterable(
    result: AsyncResult = None,
) -> Union[X, Optional[X], List[X]]:
    return iter(result)


async def __execute_select_return_async_generator(
    result: AsyncResult = None,
) -> AsyncGenerator[X, None]:
    for row in result:
        yield row
        await asyncio.sleep(0)


@decorator
async def execute_passthrough_result(func: Callable, *args, **kwargs) -> None:
    """
    Execute but do not configure how results should be fetched
    """
    session = kwargs.pop("session")
    stmt = await func(*args, **kwargs)
    return await _execute_select(
        session=session, stmt=stmt, execute=True, return_result_as_sqlalchemy_native=True
    )


@decorator
async def execute_discard_result(func: Callable, *args, **kwargs) -> None:
    """
    Execute and discard all results immediately if any
    """
    session = kwargs.pop("session")
    stmt = await func(*args, **kwargs)
    return await _execute_select(
        session=session, stmt=stmt, execute=True, return_result_discard=True
    )


@decorator
async def execute_scalar(func: Callable, *args, **kwargs) -> List[X]:
    session = kwargs.pop("session")
    stmt = await func(*args, **kwargs)
    return await _execute_select(
        session=session,
        stmt=stmt,
        execute=True,
        result_scalar=True,
        return_result_as_sqlalchemy_native=True,
    )


@decorator
async def execute_scalars_one_or_none(func: Callable, *args, **kwargs) -> Optional[X]:
    session = kwargs.pop("session")
    stmt = await func(*args, **kwargs)
    return await _execute_select(
        session=session,
        stmt=stmt,
        execute=True,
        result_scalars=True,
        result_one_or_none=True,
        return_result_as_sqlalchemy_native=True,
    )


@decorator
async def execute_scalars_one(func: Callable, *args, **kwargs) -> X:
    session = kwargs.pop("session")
    stmt = await func(*args, **kwargs)
    return await _execute_select(
        session=session,
        stmt=stmt,
        execute=True,
        result_scalars=True,
        result_one=True,
        return_result_as_sqlalchemy_native=True,
    )


@decorator
async def execute_scalars_all_iterable(func: Callable, *args, **kwargs) -> Iterable[X]:
    session = kwargs.pop("session")
    stmt = await func(*args, **kwargs)
    return await _execute_select(
        session=session,
        stmt=stmt,
        execute=True,
        result_scalars=True,
        result_all=True,
        return_result_as_sqlalchemy_native=True,
    )


@decorator
async def execute_scalars_all_async_generator(
    func: Callable, *args, **kwargs
) -> AsyncGenerator[X, None]:
    session = kwargs.pop("session")
    stmt = await func(*args, **kwargs)
    return await _execute_select(
        session=session,
        stmt=stmt,
        execute=True,
        result_scalars=True,
        result_all=True,
        return_result_as_async_generator=True,
    )


# NOTE: Not supported: https://github.com/sqlalchemy/sqlalchemy/issues/7667
# @decorator
# async def execute_scalars_stream_iterable(
#     func, max_row_buffer: int = None, *args, **kwargs
# ) -> Iterable[X]:
#     session = kwargs.pop("session")
#     stmt = await func(*args, **kwargs)
#     return await _execute_select(
#         session=session,
#         stmt=stmt,
#         execute=True,
#         # result_scalars=False,
#         result_stream=True,
#         result_stream_max_row_buffer=max_row_buffer,
#         return_result_as_iterable=True,
#     )


# NOTE: Not supported: https://github.com/sqlalchemy/sqlalchemy/issues/7667
# @decorator
# async def execute_scalars_stream_async_generator(
#     func, max_row_buffer: int = None, *args, **kwargs
# ) -> AsyncGenerator[X, None]:
#     session = kwargs.pop("session")
#     stmt = await func(*args, **kwargs)
#     return await _execute_select(
#         session=session,
#         stmt=stmt,
#         execute=True,
#         # result_scalars=False,
#         result_stream=True,
#         result_stream_max_row_buffer=max_row_buffer,
#         return_result_as_async_generator=True,
#     )
