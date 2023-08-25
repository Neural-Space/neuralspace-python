import os
import io
import asyncio
from uuid import uuid4
from pathlib import Path
from functools import partial


class AttrDict(dict):

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct=None):
        dct = dict() if not dct else dct
        for key, value in dct.items():
            if hasattr(value, 'keys'):
                value = AttrDict(value)
            self[key] = value


async def run_sync_as_async(executor, func, *args, **kwargs):
    f = partial(func, *args, **kwargs)
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(executor, f)
    return res


def run_async_as_sync(func, *args, **kwargs):
    f = partial(func, *args, **kwargs)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(f())
    return res


def get_filename(file):
    if file is None:
        raise ValueError('No file given')
    if isinstance(file, (str, Path)):
        if not os.path.exists(file):
            raise ValueError(
                f'No such file: {file}'
            )
        name = os.path.basename(file)
    elif isinstance(file, (bytes, io.IOBase)):
        name = uuid4().hex + '.wav'
    else:
        raise TypeError(
            f'Unsupported file type: {type(file)}'
        )
    return name


def get_content(file):
    if file is None:
        raise ValueError('No file given')
    if isinstance(file, (str, Path)):
        if not os.path.exists(file):
            raise ValueError(
                f'No such file: {file}'
            )
        content = open(file, 'rb')
    elif isinstance(file, (bytes, io.IOBase)):
        content = file
    else:
        raise TypeError(
            f'Unsupported file type: {type(file)}'
        )
    return content


def create_formdata_file(file):
    name = get_filename(file)
    content = get_content(file)
    data = (
        name,
        content,
        'application/octet-stream',
    )
    return data
