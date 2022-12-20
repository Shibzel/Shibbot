from dotenv import load_dotenv
import asyncio
import orjson
import time
import os
import gc
import math
import psutil
import aiohttp

from .logger import Logger


class ServerSpecifications:
    """This dumbass dev forgot to add a documentation."""

    def __init__(self, bot, loop: asyncio.AbstractEventLoop=asyncio.get_event_loop(), using_pterodactyl: bool=None, secs_looping=10.0):
        self.bot = bot
        self._loop = loop
        self.looping = True
        self.secs_looping = secs_looping

        self._max_memory = self._memory_usage = self._cpu_usage_percent = self._max_cpu_percent = self._threads = 1
        self.location: str | None = "None"

        load_dotenv()
        self.using_pterodactyl = using_pterodactyl
        if self.using_pterodactyl is None:
            self.using_pterodactyl = os.getenv("USE_PTERO_API") in ('True', '1')
        if self.using_pterodactyl:
            self._panel_url = os.getenv("PTERO_PANEL_URL")
            self._token = os.getenv("PTERO_PANEL_TOKEN")
            self._server_id = os.getenv("PTERO_PANEL_SERVER_ID")
            self.headers = {"Accept": "application/json",
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {self._token}"}
            for i in (self._panel_url, self._token, self._server_id):
                if i == "":
                    self.using_pterodactyl = False
                    Logger.warn("Missing parameters to fetch the Pterodactyl container's usage, using Psutil instead.")

        if self.using_pterodactyl:
            self._loop.create_task(self._get_specs_loop())
            self._loop.create_task(self._get_location())


    @property
    def max_memory(self):
        return psutil.virtual_memory().total/1_000_000 if not self.using_pterodactyl else self._max_memory


    @property
    def memory_usage(self):
        return psutil.virtual_memory().used/1_000_000 if not self.using_pterodactyl else self._memory_usage


    @property
    def cpu_percentage(self):
        return psutil.cpu_percent() if not self.using_pterodactyl else self._cpu_usage_percent/self._max_cpu_percent*100


    @property
    def threads(self):
        return psutil.cpu_count(logical=True) if not self.using_pterodactyl else self._threads


    async def close(self):
        self.looping = False


    async def _request(self, url):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            response = await session.get(url)
            result = (await response.json(loads=orjson.loads))
            if response.status != 200:
                raise Exception(result["warn"])
            return result


    async def _get_current(self):
        return (await self._request(f"{self._panel_url}/api/client/servers/{self._server_id}/resources"))["attributes"]["resources"]
        

    async def _get_limits(self):
        return (await self._request(f"{self._panel_url}/api/client/servers/{self._server_id}"))["attributes"]["limits"]


    async def _get_specs_loop(self):
        while self.looping:
            try:
                limits = await self._get_limits()
                self._max_memory = limits["memory"]  # In MB.
                self._max_cpu_percent = limits["cpu"]
                self._threads = limits["threads"] if limits["threads"] else math.ceil(self._max_cpu_percent/100)
            except:
                Logger.warn("Failed to obtain the bot's hardware limits on Pterodactyl.")
                
            for _ in range(int(300/self.secs_looping)):
                try:
                    current = await self._get_current()
                    self._memory_usage = current["memory_bytes"]/1_000_000 # Bytes -> MB
                    self._cpu_usage_percent = current["cpu_absolute"]
                except:
                    if self.bot.is_alive:
                        Logger.warn("Failed to obtain the bot's hardware usage on Pterodactyl.")
                await asyncio.sleep(self.secs_looping)


    async def _get_location(self):
        async with aiohttp.ClientSession() as session:
            got_response = False
            while not got_response:
                try:
                    result = await session.get("http://ip-api.com/json/?fields=country,city")
                    json_result = await result.json(loads=orjson.loads)
                    self.location = f"{json_result['city']}, {json_result['country']}"
                    got_response = True
                except:
                    await asyncio.sleep(40)

            
async def auto_gc(specs: ServerSpecifications, sleep: int = 60, max_percentage: float = 90.0):
    while True:
        await asyncio.sleep(sleep)
        percentage = specs.memory_usage/specs.max_memory*100
        if percentage > max_percentage:
            gc.collect()