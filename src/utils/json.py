from asyncio import gather
from aiohttp import ClientSession
from orjson import loads, dumps

from ..errors import ServiceUnavailableError


JsonObject = list | dict[str] # Just to indicate that it's an Json object, nothing special.

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
            return [await response.json(loads=loads) for response in await gather(*[session.get(url) for url in urls])]
    except Exception:
        raise ServiceUnavailableError()