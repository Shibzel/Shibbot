import discord
from discord.ext import bridge, commands
from aiohttp import ClientSession
from orjson import loads

from src.core import Shibbot
from src.models.cog import PluginCog
from src.errors import ServiceUnavailableError, MissingArgumentsError

from . import English, French


PLUGIN_NAME = "utils"

class Utilities(PluginCog):
    def __init__(self, bot):
        self.bot: Shibbot = bot
        super().__init__(
            plugin_name=PLUGIN_NAME,
            name={"en": "Utilities", "fr": "Utilitaires"},
            description={"en": "A variety of commands.", "fr": "Un ensemble de commandes variées."},
            languages={"en": English, "fr": French}, emoji="🔍"
        )

    @staticmethod
    async def req_short_url(service_url, url_to_shorten):
        async with ClientSession() as session:
            response = await session.get(url=service_url, params={'format': 'json', 'url': url_to_shorten,})
            result = loads(await response.text()) # Somehow await response.json() doesn't work here.
            if result.get("errorcode"):
                error_code = result["errorcode"]
                if error_code in (1, 2): raise commands.BadArgument
                if error_code in (3, 4): raise ServiceUnavailableError
            return result
        
    @bridge.bridge_command(name="shorturl", aliases=["short"], description="Shorten a URL link.", description_localizations={"fr": "Raccourcit un lien URL."},
                           options=[discord.Option(name="url", description="The link to shorten.", description_localizations={"fr": "Le lien à raccourcir."})])
    @commands.cooldown(1, 7, commands.BucketType.default)
    async def shorten_url(self, ctx: bridge.BridgeContext, url: str = None):
        if not url:
            raise MissingArgumentsError(ctx.command)
        
        try: 
            result = await self.req_short_url("https://is.gd/create.php", url)
        except ServiceUnavailableError: 
            result = await self.req_short_url("https://v.gd/create.php", url)
        except commands.BadArgument:
            lang = await self.get_lang(ctx)
            raise MissingArgumentsError(ctx.command, error_case_msg=lang.SHORTEN_URL_WRONG_URL)
        await ctx.respond(content=result["shorturl"])