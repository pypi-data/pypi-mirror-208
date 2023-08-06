import asyncio
import functools
from typing import Awaitable, Callable, Union
from typing_extensions import ParamSpec, TypeVar


T = TypeVar("T")
P = ParamSpec("P")


def is_coro_func(func: Union[Callable[P, T], Callable[P, Awaitable[T]]]) -> bool:
    """Check the function a coroutine function or not.

    Parameters
    ----------
    func : Union[Callable[P, T], Callable[P, Awaitable[T]]]
        The input function.

    Returns
    -------
    bool
        The function is coroutine function.

    Raises
    ------
    ValueError
        The input is not callable.
    """

    if not callable(func):
        raise ValueError(f"The {func} is not callable.")

    output = False

    if isinstance(func, functools.partial):
        if asyncio.iscoroutinefunction(func.func):
            output = True

    elif asyncio.iscoroutinefunction(func):
        output = True

    else:
        if hasattr(func, "__call__") and asyncio.iscoroutinefunction(func.__call__):
            output = True

    return output
