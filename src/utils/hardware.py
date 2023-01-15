from gc import collect
from math import ceil
from psutil import cpu_count, cpu_percent, virtual_memory
from aiohttp import ClientSession
from asyncio import sleep as async_sleep, AbstractEventLoop
from datetime import datetime
from orjson import loads

from ..logging import Logger


logger = Logger(__name__)

class Uptime:
    def __init__(self, init_time: float):
        now = datetime.utcnow()
        self._delta = now - init_time
        hours, remainder = divmod(int(self._delta.total_seconds()), 3600)
        days, hours = divmod(hours, 24)
        minutes, seconds = divmod(remainder, 60)

        self.seconds = seconds
        self.minutes = minutes
        self.hours = hours
        self.days = days

    def __repr__(self) -> str:
        return f"<{__name__}.{type(self).__name__} delta={self._delta}>"
    
    def __str__(self) -> str:
        return f"{__name__}.{type(self).__name__}(days={self.days}, hours={self.hours}, minutes={self.minutes}, seconds={self.seconds})"

class ServerSpecifications:
    """This dumbass dev forgot to add a documentation."""

    def __init__(self, bot, using_ptero: bool = False, ptero_url: str = None, ptero_token: str = None, ptero_server_id: str = None, secs_looping: float = 15.0,):
        self.bot = bot
        self._loop: AbstractEventLoop = bot.loop
        self.using_pterodactyl = using_ptero
        self._panel_url = ptero_url
        self._token = ptero_token
        self._server_id = ptero_server_id
        self.secs_looping = secs_looping
        self._headers = {"Accept": "application/json",
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self._token}"}
        self.looping = True
        self._max_memory = self._memory_usage = self._cpu_usage_percent = self._max_cpu_percent = self._threads = 1
        self.location: str | None = "None"

    @property
    def max_memory(self):
        return virtual_memory().total/1_000_000 if not self.using_pterodactyl else self._max_memory

    @property
    def memory_usage(self):
        return virtual_memory().used/1_000_000 if not self.using_pterodactyl else self._memory_usage

    @property
    def cpu_percentage(self):
        return cpu_percent() if not self.using_pterodactyl else self._cpu_usage_percent/self._max_cpu_percent*100

    @property
    def threads(self):
        return cpu_count(logical=True) if not self.using_pterodactyl else self._threads
    
    def start(self):
        if self.using_pterodactyl:
            logger.debug("Beginning to retrieve server hardware usage on the Pterodactyl API.")
            self._loop.create_task(self._get_specs_loop())
        self._loop.create_task(self._get_location())

    async def close(self):
        self.looping = False

    async def _request(self, url):
        async with ClientSession(headers=self._headers) as session:
            response = await session.get(url)
            result = (await response.json(loads=loads))
            if response.status != 200:
                raise Exception(result)
            return result

    async def _get_current(self):
        return (await self._request(f"{self._panel_url}/api/client/servers/{self._server_id}/resources"))["attributes"]["resources"]

    async def _get_limits(self):
        return (await self._request(f"{self._panel_url}/api/client/servers/{self._server_id}"))["attributes"]["limits"]

    async def _get_specs_loop(self):
        show_error = True
        while self.looping:
            try:
                limits = await self._get_limits()
                self._max_memory = limits["memory"]  # In MB.
                self._max_cpu_percent = limits["cpu"]
                self._threads = limits["threads"] if limits["threads"] else ceil(self._max_cpu_percent/100)
                show_error = True
            except Exception as e:
                if show_error:
                    logger.error("Failed to obtain the bot's hardware limits on Pterodactyl.", e)
                    show_error = False
            for _ in range(int(300/self.secs_looping)):
                sleep = self.secs_looping
                try:
                    current = await self._get_current()
                    self._memory_usage = current["memory_bytes"]/1_000_000 # Bytes -> MB
                    self._cpu_usage_percent = current["cpu_absolute"]
                    show_error = True
                except Exception as e:
                    if show_error:
                        logger.error("Failed to obtain the bot's hardware usage on Pterodactyl.", e)
                        show_error = False
                await async_sleep(sleep)

    async def _get_location(self):
        async with ClientSession() as session:
            logger.debug("Trying to get the location of the machine.")
            got_response = False
            while not got_response:
                try:
                    result = await session.get("http://ip-api.com/json/?fields=country,city")
                    json_result = await result.json(loads=loads)
                    self.location = f"{json_result['city']}, {json_result['country']}"
                    logger.debug(f"Got location '{self.location}'.")
                    got_response = True
                except:
                    await async_sleep(40)
            
async def auto_gc(specs: ServerSpecifications, _sleep: int = 60, max_percentage: float = 80.0):
    while True:
        await async_sleep(_sleep)
        percentage = specs.memory_usage/specs.max_memory*100
        if percentage > max_percentage:
            logger.warn(f"Running GC, memory usage exceeding {specs.max_memory/100*max_percentage:.2f}MB (using {specs.memory_usage:.2f} out of {specs.max_memory:.2f}MB, {percentage:.2f}%).")
            collect()