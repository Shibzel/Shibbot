import discord
from discord.ext import bridge, commands
from aiohttp import ClientSession
from orjson import loads
import aiogtrans
import asyncio

from src.core import Shibbot
from src.models.cog import PluginCog
from src.errors import ServiceUnavailableError, MissingArgumentsError
from src.constants import LANGUAGES

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
    async def shorten_url(self, ctx: bridge.BridgeApplicationContext, url: str = None):
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
    
    @bridge.bridge_command(name="translate", aliases=["trans"], description="Tranlates text.", description_localizations={"fr": "Traduit du texte."},
                           options=[discord.Option(name="language", name_localizations={"fr": "langage"},
                                                   description="The language code (ex: 'fr', 'en').", description_localizations={"fr": "Le code de langage (ex: 'fr', 'en')."}),
                                    discord.Option(name="sentence", name_localizations={"fr": "phrase"},
                                                   description="The text to translate.", description_localizations={"fr": "Le texte à traduire."})])
    @commands.cooldown(1, 7, commands.BucketType.default)
    async def translate_text(self, ctx: bridge.BridgeApplicationContext, language: str = None, *, sentence: str = None):
        if not language or not sentence:
            raise MissingArgumentsError(ctx.command)
        for i in LANGUAGES.items():
            if language not in i:
                lang = await self.get_lang(ctx)
                raise MissingArgumentsError(ctx.command, lang.TRANSLATE_TEXT_LANG_CODE_ERR)
            
        async with ctx.typing():
            try:
                async with aiogtrans.GoogleTrans(target=language) as translator:
                    result = await asyncio.wait_for(translator.translate(text=sentence), 5)
            except aiogtrans.UnsupportedLanguage:
                raise MissingArgumentsError(ctx.command, error_case_msg="")
            except (aiogtrans.RequestError, aiogtrans.TooManyRequests, asyncio.TimeoutError):
                raise ServiceUnavailableError
            
        lang = await self.get_lang(ctx)
        embed = discord.Embed(color=0x4b8cf5)
        embed.set_author(name=lang.TRANSLATE_TEXT_TITLE, icon_url="https://www.googlewatchblog.de/wp-content/uploads/google-translate-logo-1024x1024.png")
        embed.add_field(name=lang.TRANSLATE_TEXT_ORIGINAL, value=sentence, inline=False)
        embed.add_field(name=lang.TRANSLATE_TEXT_TRANSLATED, value=result, inline=False)
        embed.set_footer(text=lang.DEFAULT_FOOTER.format(user=ctx.author), icon_url=ctx.author.avatar)

        await ctx.respond(embed=embed)