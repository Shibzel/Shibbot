import psutil
import asyncio
from math import ceil
from aiohttp import ClientSession
from datetime import datetime
from orjson import loads

from ..logging import SubLogger


class Uptime:
    def __init__(self, init_time: float):
        now = datetime.utcnow()
        self._delta = now - init_time
        hours, remainder = divmod(int(self._delta.total_seconds()), 3600)
        self.days, self.hours = divmod(hours, 24)
        self.minutes, self.seconds = divmod(remainder, 60)

    def __repr__(self) -> str:
        return f"<{__name__}.{type(self).__name__} delta={self._delta}>"

    def __str__(self) -> str:
        return f"{self.days}d, {self.hours}h, {self.minutes}m and {self.seconds}s"

class SelfLocation:
    def __init__(self, logger: SubLogger = None):
        self.logger = logger
        self.country = None
        self.city = None
        self.continent = None
        self.got_response = False
    
    def __str__(self) -> str:
        return (f"{self.city}, {self.country} ({self.continent})"
                if self.got_response else "N/A")
    
    def __await__(self):
        async def coro():
            await self.update()
            return self
        return coro().__await__()
    
    async def update(self, persist: bool = True):
        async with ClientSession() as session:
            if self.logger:
                self.logger.debug("Trying to get the location of the machine.")
            got_response = False
            while got_response is False:
                try:
                    result = await session.get("http://ip-api.com/json/?fields=continentCode,country,city")
                    json_result = await result.json(loads=loads)
                    
                    self.country = json_result["country"]
                    self.city = json_result["city"]
                    self.continent = json_result["continentCode"]
                    
                    got_response = self.got_response = True
                    self.logger.debug(f"Got location '{self}'.")
                except:
                    if not persist:
                        break
                    await asyncio.sleep(40)

class ServerSpecifications:
    def __init__(self, bot):
        self.bot = bot
        self.loop = bot.loop
        self.logger: SubLogger = bot.logger.get_logger(__name__)
        self.location = SelfLocation(self.logger)
        
        self._max_memory = None
        self._memory_usage = None
        self._threads = None
        
    @property
    def max_memory(self):
        return self._max_memory or psutil.virtual_memory().total/1024e3

    @property
    def memory_usage(self):
        return self._memory_usage or psutil.virtual_memory().used/1024e3
    
    @property
    def memory_percentage(self):
        if self._max_memory and self._memory_usage:
            return self._memory_usage/self._max_memory*100
        return psutil.virtual_memory().percent

    @property
    def cpu_percentage(self):
        return psutil.cpu_percent()

    @property
    def threads(self):
        return self._threads or psutil.cpu_count(logical=True)

    def start(self):
        self.loop.create_task(self.location.update())
        
    async def close(self):
        pass  # Does nothing, to override.

class PteroContainerSpecifications(ServerSpecifications):
    def __init__(self, bot, ptero_url: str = None, ptero_token: str = None, ptero_server_id: str = None,
                 secs_looping: float = 15.0,):
        super().__init__(bot)
        self._panel_url = ptero_url
        self._token = ptero_token
        self._server_id = ptero_server_id
        self.secs_looping = secs_looping
        self._headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token}"
        }
        self._session = ClientSession(headers=self._headers)
        self.looping = False
        
        self._cpu_usage_percent = .0
        self._max_cpu_percent = 100.
    
    @property
    def cpu_percentage(self):
        return self._cpu_usage_percent/self._max_cpu_percent*100

    def start(self):
        self.loop.create_task(self.update_loop())
        super().start()

    async def close(self):
        self.logger.debug("Closing session and loop.")
        self.looping = False
        await self._session.close()

    async def _request(self, url):
        response = await self._session.get(url)
        result = (await response.json(loads=loads))
        if response.status != 200:
            raise Exception(result)  # TODO: Generic exception, raise a more pertinent one.
        return result

    async def update_limits(self):
        url = f"{self._panel_url}/api/client/servers/{self._server_id}"
        result = await self._request(url)
        limits = result["attributes"]["limits"]
        
        self._max_memory = limits["memory"]  # In MB.
        self._max_cpu_percent = limits["cpu"]
        threads = limits["threads"]
        self._threads = threads if threads else ceil(self._max_cpu_percent/100)
        
    async def update_usage(self):
        url = f"{self._panel_url}/api/client/servers/{self._server_id}/resources"
        result = await self._request(url)
        current = result["attributes"]["resources"]
        
        self._memory_usage = current["memory_bytes"]/1_000_000  # Bytes -> MB
        self._cpu_usage_percent = current["cpu_absolute"]
        
    async def update_loop(self, loop_time: float = 300.):
        if self.looping:
            raise RuntimeError("The update loop is already running.")
        
        self.logger.debug("Beginning to retrieve server hardware usage on the Pterodactyl API.")
        self.looping = True
        notify = True
        
        async def _try(coro, error_message: str):
            nonlocal notify
            try:
                await coro
                notify = True
            except Exception as err:
                if notify:
                    self.logger.error(error_message, err)
                    notify = False
        
        while self.looping:
            await _try(self.update_limits(),
                 error_message="Failed to obtain the bot's hardware limits on Pterodactyl.")
            
            for _ in range(int(loop_time/self.secs_looping)):
                await _try(self.update_usage(),
                     error_message="Failed to obtain the bot's hardware usage on Pterodactyl.")
                await asyncio.sleep(self.secs_looping)
                