import copy
import glob
import json
from pathlib import Path
from typing import Dict, Generator, List, Optional, Text, Tuple, Union

from pyassorted.asyncio.io import aio_open


def merge_objects(
    obj_1: Union[Dict, List],
    obj_2: Union[Dict, List],
    inplace: bool = False,
) -> Union[Dict, List]:
    out = obj_1
    if inplace is False:
        out = copy.deepcopy(obj_1)
        obj_2 = copy.deepcopy(obj_2)

    if isinstance(out, Dict) and isinstance(obj_2, Dict):
        for _k, _v in obj_2.items():
            if _k in out:
                out[_k] = merge_objects(out[_k], _v, inplace=inplace)
            else:
                out[_k] = _v

    elif isinstance(out, List) and isinstance(obj_2, List):
        out.extend(obj_2)

    else:
        raise TypeError(f"Cannot merge {type(obj_1)} with {type(obj_2)}")

    return out


def merge_all_objects(
    *objects: Union[Dict, List],
    inplace: bool = False,
) -> Optional[Union[Dict, List]]:
    if not objects:
        return None
    obj = objects[0]
    for other_obj in objects[1:]:
        obj = merge_objects(obj, other_obj, inplace=inplace)
    return obj


def read_json(filepath: Text) -> Union[Dict, List]:
    with open(filepath, "r") as f:
        return json.load(f)


async def async_read_json(filepath: Text) -> Union[Dict, List]:
    async with aio_open(filepath, "r") as f:
        _data = await f.read()
        return json.loads(_data)


def read_json_recursively(
    dirpath: Union[Path, Text]
) -> Generator[Tuple[Text, Union[Dict, List]], None, None]:
    dirpath = Path(dirpath)
    if dirpath.exists() and dirpath.is_file():
        yield read_json(dirpath)
        return
    filepaths = sorted(
        [filepath for filepath in glob.iglob(f"{dirpath}/**/*.json", recursive=True)]
    )
    for filepath in filepaths:
        yield (filepath, read_json(filepath))


async def async_read_json_recursively(dirpath: Union[Path, Text]):
    dirpath = Path(dirpath)
    if dirpath.exists() and dirpath.is_file():
        _data = await async_read_json(dirpath)
        yield _data
        return
    filepaths = sorted(
        [filepath for filepath in glob.iglob(f"{dirpath}/**/*.json", recursive=True)]
    )
    for filepath in filepaths:
        yield (filepath, (await async_read_json(filepath)))


def merge_json_recursively(dirpath: Union[Path, Text]) -> Union[Dict, List]:
    dirpath = Path(dirpath)

    obj = {}
    for _, _data in read_json_recursively(dirpath):
        obj = merge_objects(obj, _data)
    return obj
