import orjson
import aiohttp
import asyncio


async def dump(_object: object, fpath: str, *args, **kwargs) -> None:
    """Writes a json file, wow."""
    with open(fpath, "wb+") as out_file:
        out_file.write(orjson.dumps(_object, *args, **kwargs))

async def load(fpath: str):
    """Loads a json file, incredible."""
    with open(fpath, "rb") as json_file:
        return orjson.loads(json_file.read())


async def json_from_urls(urls: list) -> list:
    """Asynchronous way to get the json content from an API."""
    async with aiohttp.ClientSession() as session:
        return [await response.json(loads=orjson.loads) for response in await asyncio.gather(*[session.get(url) for url in urls])]
