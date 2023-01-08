from asyncio import gather
from aiohttp import ClientSession
from json import dump as _dump, load as _load


async def dump(_object: object, fpath: str, *args, **kwargs) -> None:
    """Writes a json file, wow."""
    with open(fpath, "w+") as out_file:
        _dump(_object, out_file, *args, **kwargs)

async def load(fpath: str):
    """Loads a json file, incredible."""
    with open(fpath, 'r') as json_file:
        return _load(json_file)

async def json_from_urls(urls: list, *args, **kwargs) -> list:
    """Asynchronous way to get the json content from an API."""
    async with ClientSession(*args, **kwargs) as session:
        return [await response.json() for response in await gather(*[session.get(url) for url in urls])]
