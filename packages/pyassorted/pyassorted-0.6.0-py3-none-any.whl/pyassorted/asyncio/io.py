import asyncio
from pathlib import Path
from typing import Iterable, List, Optional, Text, TYPE_CHECKING

from pyassorted.asyncio import run_func

if TYPE_CHECKING:
    from _typeshed import OpenTextMode


class AsyncIOWrapper:
    def __init__(
        self,
        path: Path,
        mode: "OpenTextMode" = "r",
        encoding: Optional[Text] = None,
        **kwargs
    ):
        self.path = path
        self.mode = mode
        self.encoding = encoding
        self.kwargs = kwargs

        self.file = None

    async def __aenter__(self):
        self.file = open(
            self.path, mode=self.mode, encoding=self.encoding, **self.kwargs
        )
        return self

    async def __aexit__(self, *args):
        self.close()

    def __aiter__(self):
        return self

    async def __anext__(self):
        for line in self.file:
            await asyncio.sleep(0)
            return line
        raise StopAsyncIteration

    def close(self) -> None:
        return self.file.close()

    async def read(self, __offset: int, __whence: int = 0) -> int:
        return await run_func(self.file.seek, __offset, __whence)

    async def read(self, __size: Optional[int] = None) -> Text:
        return await run_func(self.file.read, __size)

    async def readline(self, __size: int = -1) -> Text:
        return await run_func(self.file.readline, __size)

    async def readlines(self, __hint: int = -1) -> List[Text]:
        return await run_func(self.file.readlines, __hint)

    async def seek(self, __cookie: int, __whence: int = 0) -> int:
        return await run_func(self.file.seek, __cookie, __whence)

    async def write(self, __s: Text) -> int:
        return await run_func(self.file.write, __s)

    async def writelines(self, __lines: Iterable[Text]) -> None:
        return await run_func(self.file.writelines, __lines)


def aio_open(
    path: Path, mode: "OpenTextMode" = "r", encoding: Optional[Text] = None, **kwargs
):
    """Wrapper for `open` that returns an async context manager.

    Parameters
    ----------
    path : Path
        The path to the file to open.
    mode : OpenTextMode, optional
        The mode to open the file in, by default "r"
    encoding : Optional[Text], optional
        The encoding to use, by default None

    Returns
    -------
    AsyncIOWrapper
        The async context manager.

    Raises
    ------
    ValueError
        If the mode is not a text mode.

    Examples
    --------
    >>> import asyncio
    >>> from pyassorted.io import aio_open
    >>>
    >>> async def main():
    ...    # Write to a file
    ...    async with aio_open("file.txt", "w") as f:
    ...        await f.write("Hello")
    ...    # Read file content
    ...    async with aio_open("file.txt") as f:
    ...        assert (await f.read()) == "Hello"
    >>>
    >>> asyncio.run(main())
    """

    return AsyncIOWrapper(path=path, mode=mode, encoding=encoding, **kwargs)
