import asyncio
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
