import asyncio
import functools
import concurrent.futures
from typing import Awaitable, Callable, Union
from typing_extensions import ParamSpec, TypeVar

from pyassorted.asyncio.utils import is_coro_func


T = TypeVar("T")
P = ParamSpec("P")


async def run_func(
    func: Union[Callable[P, T], Callable[P, Awaitable[T]]],
    *args,
    max_workers=1,
    **kwargs,
) -> T:
    """Run the coroutine function or run function in a thread pool.

    Parameters
    ----------
    func : Union[Callable[P, T], Callable[P, Awaitable[T]]]
        The function or coroutine function.
    max_workers : int, optional
        The worker number of thread pool, by default 1

    Returns
    -------
    Any
        The return value of the function.

    Raises
    ------
    ValueError
        The input is not callable.
    """

    if not callable(func):
        raise ValueError(f"The {func} is not callable.")

    output = None

    if is_coro_func(func):
        partial_func = functools.partial(func, *args, **kwargs)
        output = await partial_func()

    else:
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            partial_func = functools.partial(func, *args, **kwargs)
            output = await loop.run_in_executor(pool, partial_func)

    return output
