# pyassorted #

A library has assorted utils in Pure-Python. There are 3 principles:

1. Light-weight
2. No dependencies
3. Pythonic usage.


* Documentation: https://dockhardman.github.io/pyassorted/
* PYPI: https://pypi.org/project/pyassorted/

## Installation ##
```shell
pip install pyassorted
```

## Modules ##
- pyassorted.asyncio.executor
- pyassorted.asyncio.io
- pyassorted.asyncio.utils
- pyassorted.cache.cache
- pyassorted.collections.sqlitedict
- pyassorted.datetime
- pyassorted.lock.filelock


## Examples ##

### pyassorted.asyncio ###

```python
import asyncio
from pyassorted.asyncio import run_func

def normal_func() -> bool:
    return True

async def async_func() -> bool:
    await asyncio.sleep(0.0)
    return True

async main():
    assert await run_func(normal_func) is True
    assert await run_func(async_func) is True

asyncio.run(main())
```

### pyassorted.asyncio.io ###

```python
import asyncio
from pyassorted.io import aio_open

async def main():
    # Write to a file
    async with aio_open("file.txt", "w") as f:
        await f.write("Hello")
    # Read file content
    async with aio_open("file.txt") as f:
        assert (await f.read()) == "Hello"

asyncio.run(main())
```

### pyassorted.cache ###

```python
import asyncio
from pyassorted.cache import LRU, cached

lru_cache = LRU()

# Cache function
@cached(lru_cache)
def add(a: int, b: int) -> int:
    return a + b

assert add(1, 2) == 3
assert lru_cache.hits == 0
assert lru_cache.misses == 1

assert add(1, 2) == 3
assert lru_cache.hits == 1
assert lru_cache.misses == 1

# Cache coroutine
@cached(lru_cache)
async def async_add(a: int, b: int) -> int:
    await asyncio.sleep(0)
    return a + b

assert add(1, 2) == 3
assert lru_cache.hits == 2
assert lru_cache.misses == 1
```

### pyassorted.collections.sqlitedict ###

```python
import asyncio
from pyassorted.collections.sqlitedict import SqliteDict

sql_dict = SqliteDict(":memory:")
sql_dict["key"] = "value"
assert sql_dict["key"] == "value"

# Asynchronous usage
async def main():
    await sql_dict.async_set("key", "value")
    assert (await sql_dict.async_get("key")) == "value"
asyncio.run(main())
```

### pyassorted.datetime ###

- aware_datetime_now
```python
from pyassorted.datetime import aware_datetime_now, iso_datetime_now

print(aware_datetime_now())  # datetime.datetime
print(iso_datetime_now())  # Datetime ISO String
```

- Timer
```python
import time
from pyassorted.datetime import Timer

timer = Timer()
timer.click()
time.sleep(1)
timer.click()
print(round(timer.read()))  # 1

with timer:
    time.sleep(1)
print(round(timer.read()))  # 1
```

### pyassorted.lock ###

```python
from concurrent.futures import ThreadPoolExecutor
from pyassorted.lock import FileLock

number = 0
tasks_num = 100
lock = FileLock()

def add_one():
    global number
    with lock:
        number += 1

with ThreadPoolExecutor(max_workers=40) as executor:
    futures = [executor.submit(add_one) for _ in range(tasks_num)]
    for future in futures:
        future.result()

assert number == tasks_num
```
