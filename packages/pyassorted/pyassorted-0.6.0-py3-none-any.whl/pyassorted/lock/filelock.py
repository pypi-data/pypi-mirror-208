import asyncio
import tempfile
import time
import uuid
from pathlib import Path
from typing import Optional, Text

from pyassorted.asyncio import run_func


class FileLock(object):
    """Soft File lock. The lock uses a file to store the lock status.

    Examples
    --------
    >>> from concurrent.futures import ThreadPoolExecutor
    >>> from pyassorted.lock import FileLock
    >>>
    >>> number = 0
    >>> workers = 40
    >>> tasks = 100
    >>> lock = FileLock()
    >>>
    >>> def add_one():
    ...     global number
    ...     with lock:
    ...         number += 1
    >>>
    >>> with ThreadPoolExecutor(max_workers=workers) as executor:
    ...     futures = [executor.submit(add_one) for _ in range(tasks)]
    ...     for future in futures:
    >>>         future.result()
    >>>
    >>> assert number == tasks
    """

    def __init__(
        self,
        file_name: Optional[Text] = None,
        timeout: float = 10,
        delay: float = 0.05,
        lock_expire: int = 60,
    ):
        if file_name is None:
            tmp_dir = tempfile.gettempdir()
            file_name = Path(tmp_dir).joinpath(f"pyassorted-{uuid.uuid4().hex}.lock")
        self.file_name = Path(file_name).resolve()
        self.timeout = timeout
        self.delay = delay
        self.lock_expire = lock_expire

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    async def __aenter__(self):
        await self.async_acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.async_release()

    def acquire(self):
        """Acquire lock.

        Raises
        ------
        TimeoutError
            If timeout is reached.
        """

        start_time = time.time()
        while True:
            current_time = time.time()

            # Timeout
            if current_time - start_time >= self.timeout:
                raise TimeoutError(f"Timeout after {self.timeout} seconds")

            # Expire lock
            try:
                if current_time - self.file_name.stat().st_mtime > self.lock_expire:
                    self.file_name.touch(exist_ok=False)
                    return
            except FileNotFoundError:
                pass  # File is deleted by other process or not exist.
            except FileExistsError:
                pass  # File is created before file touching.

            # Acquire lock
            try:
                self.file_name.touch(exist_ok=False)
                return
            except FileExistsError:
                pass  # The priority was preempted by other processes.

            # Delay
            time.sleep(self.delay)

    def release(self):
        """Release lock."""

        self.file_name.unlink(missing_ok=True)

    async def async_acquire(self):
        """Acquire lock.

        Raises
        ------
        TimeoutError
            If timeout is reached.
        """

        start_time = time.time()
        while True:
            current_time = time.time()

            # Timeout
            if current_time - start_time >= self.timeout:
                raise TimeoutError(f"Timeout after {self.timeout} seconds")

            # Expire lock
            try:
                file_stat = await run_func(self.file_name.stat)
                if current_time - file_stat.st_mtime > self.lock_expire:
                    await run_func(self.file_name.touch, exist_ok=False)
                    return
            except FileNotFoundError:
                pass  # File is deleted by other process or not exist.
            except FileExistsError:
                pass  # File is created before file touching.

            # Acquire lock
            try:
                await run_func(self.file_name.touch, exist_ok=False)
                return
            except FileExistsError:
                pass  # The priority was preempted by other processes.

            # Delay
            await asyncio.sleep(self.delay)

    async def async_release(self):
        """Release lock."""

        await run_func(self.file_name.unlink, missing_ok=True)

    def __del__(self):
        self.release()
