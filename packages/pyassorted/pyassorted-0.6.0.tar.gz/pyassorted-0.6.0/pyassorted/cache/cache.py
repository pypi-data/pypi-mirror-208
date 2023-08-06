from abc import ABC
from collections import OrderedDict
from threading import RLock
from typing import Any, Callable, Dict, Optional, Tuple, Type, TypeVar, Union

from pyassorted.asyncio import is_coro_func


KeyType = TypeVar("KeyType")
ValueType = TypeVar("ValueType")
EmptyType = TypeVar("EmptyType")

EMPTY_CACHE: EmptyType = object()


class CacheObject(ABC):
    """Base class for cache objects."""

    def get(self, key: KeyType) -> Union[ValueType, EmptyType]:
        raise NotImplementedError

    def put(self, key: KeyType, value: ValueType):
        raise NotImplementedError


class LRU(CacheObject):
    """Least Recently Used (LRU) cache implemented with collections.OrderedDict.

    Examples
    --------
    >>> lru_cache = LRU(init_cache={"a": "a"})
    >>> lru_cache.get("a") == "a"
    >>> assert lru_cache.hits == 1

    >>> # Init cache with LRU
    >>> new_lru_cache = LRU(init_cache=lru_cache)
    >>> new_lru_cache.get("a") == "a"
    >>> assert new_lru_cache.hits == 1
    """

    def __init__(
        self,
        maxsize: int = 0,
        init_cache: Optional[Union["LRU", Dict[KeyType, ValueType]]] = None,
        sentinel: Optional[Any] = None,
    ):
        """Least Recently Used (LRU) cache implemented with collections.OrderedDict.

        Parameters
        ----------
        maxsize : int, optional
            Maximum size of the cache, by default 0
        init_cache : Optional[Union["LRU", Dict[KeyType, ValueType]]], optional
            Initial cache, by default None. If LRU, it will share the same cache.
        sentinel : Optional[Any], optional
            Sentinel value, by default None

        Raises
        ------
        ValueError
            If initiating cache is larger than maxsize.
        """

        self.maxsize = 0 if maxsize < 0 else maxsize

        init_cache = OrderedDict() if init_cache is None else init_cache
        if self.maxsize > 0 and len(init_cache) > self.maxsize:
            raise ValueError("Initiating cache is larger than maxsize.")
        if isinstance(init_cache, LRU):
            self.cache: OrderedDict[KeyType, ValueType] = init_cache.cache
        else:
            self.cache = OrderedDict(init_cache)

        self.hits = 0
        self.misses = 0
        self.lock = RLock()
        self.sentinel = EMPTY_CACHE if sentinel is None else sentinel

    def __len__(self):
        return len(self.cache)

    def full(self) -> bool:
        """Check if cache is full.

        Returns
        -------
        bool
            True if cache is full, False otherwise.
        """

        return self.maxsize > 0 and len(self.cache) >= self.maxsize

    def get(self, key: KeyType) -> Union[ValueType, EmptyType]:
        """Get value from cache.

        Parameters
        ----------
        key : KeyType
            Key to get value from.

        Returns
        -------
        Union[ValueType, EmptyType]
            Value if key exists, otherwise sentinel.
        """

        value = self.cache.get(key, self.sentinel)

        with self.lock:
            if value is self.sentinel:
                self.misses += 1
                return self.sentinel
            else:
                self.hits += 1
                self.cache.move_to_end(key)
                return value

    def put(self, key: KeyType, value: ValueType):
        """Put value into cache.

        Parameters
        ----------
        key : KeyType
            Key to put value into.
        value : ValueType
            Value to put into cache.
        """

        if key in self.cache:
            with self.lock:
                self.cache.move_to_end(key)
                return

        with self.lock:
            self.cache[key] = value
            if self.maxsize > 0 and len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)


def make_key(args: Tuple[Any], kwargs: Dict, kw_mark: Tuple[Any] = (object(),)) -> int:
    """Make key from arguments.

    Parameters
    ----------
    args : Tuple[Any]
        Arguments.
    kwargs : Dict
        Keyword arguments.
    kw_mark : Tuple[Any], optional
        keyword arguments separator, by default (object(),)

    Returns
    -------
    int
        Hash of the key.
    """

    key = args
    if kwargs:
        key += kw_mark
        for item in kwargs.items():
            key += item
    return hash(key)


def cached(cache: Optional[Union[Type["CacheObject"], Callable]] = None):
    """Decorator to cache function calls.

    Parameters
    ----------
    cache : Optional[Union[Type["CacheObject"], Callable]], optional
        Cache object or function to cache, by default None.
        If cache variable is a to-be decorated function, a LRU cache will be used.

    Returns
    -------
    Callable
        Decorated function.

    Examples
    --------
    >>> # Cache function calls
    >>> @cached()
    >>> def add(a: int, b: int) -> int:
    ...     return a + b
    >>> assert add(1, 2) == 3
    >>> assert lru_cache.hits == 0
    >>> assert lru_cache.misses == 1
    >>> assert add(1, 2) == 3
    >>> assert lru_cache.hits == 1
    >>> assert lru_cache.misses == 1

    >>> # Cache function without decorator initialization
    >>> @cached
    >>> def random_int(a: int, b: int) -> int:
    ...     import random
    ...     return random.randint(a, b)
    >>> random_int(0, 2**32)
    >>> assert random_int(0, 2**32) == random_int(0, 2**32)

    >>> # Cache coroutine function calls
    >>> import asyncio
    >>> async def cached_in_coro_func():
    >>>     @cached()
    >>>     async def add(a: int, b: int) -> int:
    ...         await asyncio.sleep(0)
    ...         return a + b
    >>>     assert await add(1, 2) == 3
    >>>     assert lru_cache.hits == 0
    >>>     assert lru_cache.misses == 1
    >>>     assert await add(1, 2) == 3
    >>>     assert lru_cache.hits == 1
    >>>     assert lru_cache.misses == 1
    >>> asyncio.run(cached_in_coro_func())

    >>> # Cache coroutine function without decorator initialization
    >>> async def cached_in_coro_func_without_init_decorator():
    >>>     @cached
    >>>     async def random_int(a: int, b: int) -> int:
    ...         await asyncio.sleep(0)
    ...         import random
    ...         return random.randint(a, b)
    >>>     await random_int(0, 2**32)
    >>>     assert await random_int(0, 2**32) == await random_int(0, 2**32)
    >>> asyncio.run(cached_in_coro_func_without_init_decorator())
    """

    if isinstance(cache, Callable):
        func: Callable = cache
        cache = LRU()

        def wrapper(*args, **kwargs):
            key = make_key(args=args, kwargs=kwargs)
            value = cache.get(key)

            if value is cache.sentinel:
                value = func(*args, **kwargs)
                cache.put(key, value)

            return value

        async def async_wrapper(*args, **kwargs):
            key = make_key(args=args, kwargs=kwargs)
            value = cache.get(key)

            if value is cache.sentinel:
                value = await func(*args, **kwargs)
                cache.put(key, value)

            return value

        if is_coro_func(func):
            return async_wrapper
        else:
            return wrapper

    else:
        if cache is None:
            cache = LRU()

        def decorator(func):
            def wrapper(*args, **kwargs):
                key = make_key(args=args, kwargs=kwargs)
                value = cache.get(key)

                if value is cache.sentinel:
                    value = func(*args, **kwargs)
                    cache.put(key, value)

                return value

            async def async_wrapper(*args, **kwargs):
                key = make_key(args=args, kwargs=kwargs)
                value = cache.get(key)

                if value is cache.sentinel:
                    value = await func(*args, **kwargs)
                    cache.put(key, value)

                return value

            if is_coro_func(func):
                return async_wrapper
            else:
                return wrapper

        return decorator
