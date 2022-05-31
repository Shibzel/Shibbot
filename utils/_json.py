import asyncio
import os

try:
    from orjson import load as _load, dumps as _dumps  # Faster than json
except ImportError:
    from json import load as _load, dumps as _dumps
import aiohttp


def dump(_object:object, fpath:str, *args, **kwargs) -> None:
    """Writes a json file, wow."""
    with open(fpath, "wb+") as out_file:
        out_file.write(_dumps(_object, *args, **kwargs))


def load(fpath:str):
    """Loads a json file, incredible."""
    with open(fpath, "rb") as json_file:
        return _loads(json_file.read())


async def fetch_from_urls(urls: list):
    """Asynchronous way to get the json content from an API."""
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        results = []
        for response in responses:
            results.append(await response.json(loads=orjson.loads))
        return results
