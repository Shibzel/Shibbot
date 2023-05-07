import asyncio
import os
from aiohttp import ClientSession
from orjson import loads, dumps

from ..errors import ServiceUnavailableError


# Just to indicate that it's an Json object, nothing special.
JsonObject = list | dict[str]


def dump(_object: object, fpath: str, *args, **kwargs) -> None:
    """Writes a json file, wow."""
    with open(fpath, "wb+") as out_file:
        out_file.write(dumps(_object, *args, **kwargs))


def load(fpath: str) -> JsonObject:
    """Loads a json file, incredible."""
    with open(fpath, 'rb') as json_file:
        return loads(json_file.read())


async def json_from_urls(urls: list, *args, **kwargs) -> list[JsonObject]:
    """Asynchronous way to get the json content from an API."""
    try:
        async with ClientSession(*args, **kwargs) as session:
            return [await response.json(loads=loads)
                    for response in await asyncio.gather(*[session.get(url) for url in urls])]
    except Exception as exc:  # TODO: Change this general exception
        raise ServiceUnavailableError from exc


class StorageCacheHandler:
    def __init__(self, bot, fp: str):
        self.bot = bot
        self.path = fp

    @property
    def caching(self) -> bool:
        return self.bot.caching

    def store(self, obj: JsonObject = {}, convert: type = None, force: bool = False) -> None:
        if self.caching or force:
            if convert:
                obj = convert(obj)
            dump(obj, self.path)

    def get(self, default: JsonObject = None, convert: type = None) -> JsonObject:
        if os.path.exists(self.path):
            if obj := load(self.path):
                if convert:
                    obj = convert(obj)
                return obj
        return default
