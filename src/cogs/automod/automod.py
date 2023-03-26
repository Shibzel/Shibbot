import discord
from discord.ext import tasks
from aiohttp import ClientSession
import orjson
import asyncio

from src.core import Shibbot
from src.models import PluginCog
from src.utils.json import StorageCacheHandler
from src.utils.re import get_urls, url_to_domain
from src.constants import TEMPORARY_CACHE_PATH
from src.logging import Logger
from src.database import AsyncDB
from src.errors import CogDependanceMissing

from . import __name__ as cog_module_name
try:
    from ..mod import Moderation
except ImportError:
    Moderation = None


logger = Logger(cog_module_name)

PLUGIN_NAME = "automod"
SUS_DOMAINS_FP = TEMPORARY_CACHE_PATH + "/sus_links.json"


class Automod(PluginCog):
    def __init__(self, bot):
        self.bot: Shibbot = bot
        super().__init__(
            plugin_name=PLUGIN_NAME,
            name={"en": "Auto-moderation", "fr": "Auto-modération"},
            description={"en": "Automates moderation on your server.",
                         "fr": "Automatise la modération sur votre serveur."},
            languages={}, emoji="🤖"
        )
        self.sus_domains = set()
        self._mod_cog = None
        self.on_cooldown = {}
        
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.plugin_name} (
            guild_id    INTEGER PRIMARY KEY,
            profanity   BOOLEAN,
            sus_domains BOOLEAN,
            cooldown    BOOLEAN,
            nudity      BOOLEAN
        )"""
        self.bot.db.execute(query) # VER: v1.0.0
        self.bot.db.commit()
        
    @property
    def mod_cog(self) -> Moderation:
        return self._mod_cog
    
    @mod_cog.setter
    def mod_cog(self, value):
        logger.debug(f"Setting '{value}' as moderation cog for automod.")
        self._mod_cog = value

    async def when_ready(self):
        if not self.mod_cog:
            for cog in self.bot.cogs.values():
                if isinstance(cog, Moderation):
                    self.mod_cog = cog
                    break
            else:
                self.cog_unload()
                raise CogDependanceMissing(Moderation)
        
        self.update_sus_domains.start()
        
    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.content and not message.attachments:
            return
                
        async with AsyncDB() as db:
            if not await db.plugin_is_enabled(message.guild, PLUGIN_NAME, guild_only=True):
                return
            query = f"SELECT profanity, sus_domains, cooldown, nudity FROM {self.plugin_name} WHERE guild_id=?"
            async with db.conn.execute(query, (message.guild.id,)) as cursor:
                if result := await cursor.fetchone():
                    profanity, sus_domains, cooldown, nudity = result
                else:
                    return
        
            tasks = []
            if cooldown:
                tasks.append(self.check_cooldown(message))
            if message.content:
                if profanity:
                    tasks.append(self.check_profanity(message))
                if sus_domains:
                    tasks.append(self.check_domains(message))
            if message.attachments:
                if nudity and not message.channel.is_nsfw():
                    tasks.append(self.check_nudity(message))
                
            if tasks:
                await asyncio.gather(*tasks)
    
    async def check_cooldown(self, message: discord.Message):
        pass
        
    async def check_profanity(self, message: discord.Message):
        pass
    
    async def check_domains(self, message: discord.Message):
        urls = get_urls(message.content)
        all_domains = []
        for url in urls:
            all_domains += url_to_domain(url)
        
        if set(all_domains) & self.sus_domains:
            pass # TODO: log and action
    
    async def check_nudity(self, message: discord.Message):
        pass

    @tasks.loop(hours=12)
    async def update_sus_domains(self):
        logger.debug("Updating list of scam domains.")
        cache_handler = StorageCacheHandler(self.bot, SUS_DOMAINS_FP)
        if not self.sus_domains:
            self.sus_domains = cache_handler.get(self.sus_domains, convert=set)
        async with ClientSession() as session:
            request = await session.get(
                "https://raw.githubusercontent.com/Discord-AntiScam/scam-links/main/urls.json")
            if request.status != 200:
                await asyncio.sleep(3600)
                await self.update_sus_domains()
            # Somehow using await request.json() cause the func to stop and loop forever
            response = orjson.loads(await request.text())
        new_set = set(response)
        additions, deletions = new_set - self.sus_domains, self.sus_domains - new_set
        if additions or deletions:
            self.sus_domains = new_set
            cache_handler.store(response)
            logger.debug(f"Updated list of scam domains ({len(additions)} additions,"
                         f" {len(deletions)} deletions, total: {len(self.sus_domains)}).")
