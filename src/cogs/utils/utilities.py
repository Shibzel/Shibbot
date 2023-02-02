import discord
from discord.ext import bridge, commands
from aiohttp import ClientSession
from orjson import loads
import aiogtrans
import asyncio
from aiowiki import Wiki

from src import database
from src.core import Shibbot
from src.models import PluginCog, EmbedViewer, CustomView
from src.errors import ServiceUnavailableError, MissingArgumentsError, NotInteractionOwner
from src.constants import LANGUAGES
from src.utils import get_language

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
        if language not in LANGUAGES or language not in LANGUAGES.values():
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
        embed.set_author(name="Translate", icon_url="https://www.googlewatchblog.de/wp-content/uploads/google-translate-logo-1024x1024.png")
        embed.add_field(name=lang.TRANSLATE_TEXT_ORIGINAL, value=sentence, inline=False)
        embed.add_field(name=lang.TRANSLATE_TEXT_TRANSLATED, value=result, inline=False)
        embed.set_footer(text=lang.DEFAULT_FOOTER.format(user=ctx.author), icon_url=ctx.author.avatar)

        await ctx.respond(embed=embed)
        
    @bridge.bridge_command(name="urbandict", aliases=["udict"], description="Gives the definition of a word on Urban Dictionary.",)
    @discord.option(name="word", description="The word you want the definition of.")
    async def urbdict_search(self, ctx: bridge.BridgeApplicationContext, *, word: str = None):
        url = "https://api.urbandictionary.com/v0/" + (f"define?term={word}" if word else "random")
        async with ClientSession() as session:
            request = await session.get(url)
            if request.status != 200: raise ServiceUnavailableError()
            response = (await request.json(loads=loads))["list"]
        if response == []:
            raise commands.BadArgument
        to_order = {d["thumbs_up"]: d for d in response} # TODO: Optimize this sorting algorithm with sorted()
        order = list(to_order.keys())
        order.sort()
        definitions = [to_order[i] for i in order[::-1]]
            
        def clean_string(string: str):
            return string.replace("[", "**").replace("]", "**").replace("\n\n", "\n")
        embeds = []
        for definition in definitions:
            embed = discord.Embed(color=0x2faaee)
            embed.set_author(name="Urban Dictionary", url=definition["permalink"],
                             icon_url="https://slack-files2.s3-us-west-2.amazonaws.com/avatars/2018-01-11/297387706245_85899a44216ce1604c93_512.jpg")
            _def = clean_string(definition["definition"])
            example = clean_string(definition["example"])
            embed.add_field(name=f"Definition of \"{definition['word']}\" (by {definition['author']})", value=_def if len(_def) <= 1024 else _def[:1021]+"...", inline=False)
            embed.add_field(name="Example", value=example if len(example) <= 1024 else example[:1021]+"...", inline=False)
            embed.set_footer(icon_url=ctx.author.avatar, text=English.DEFAULT_FOOTER.format(user=ctx.author) + f" | 👍 {definition['thumbs_up']} • 👎 {definition['thumbs_down']}")
            embeds.append(embed)
        
        next_button = discord.ui.Button(style=discord.ButtonStyle.blurple, label="Next Definition")
        previous_button = discord.ui.Button(style=discord.ButtonStyle.gray, label="Previous Definition")
        embed_viewer = self.bot.add_bot(EmbedViewer(embeds, next_button, previous_button, use_extremes=True))
        await embed_viewer.send_message(ctx)
        
    @bridge.bridge_command(name="wikipedia", aliases=["wiki"]) # TODO: Add a description
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def search_on_wikipedia(self, ctx: bridge.BridgeApplicationContext, article: str = None):
        lang_code = await database.get_language(ctx)
        lang = get_language(self.languages, lang_code)
        if not article:
            raise MissingArgumentsError(ctx.command)

        wiki = Wiki.wikipedia(lang_code)
        try: propositions = await asyncio.wait_for(wiki.opensearch(article, limit=25), 5)
        except: raise ServiceUnavailableError
        if not propositions:
            await wiki.close()
            raise commands.BadArgument
        embed = discord.Embed(description=lang.SEARCH_ON_WIKIPEDIA_DESCRIPTION, color=0xffffff)
        embed.set_author(name="Wikipedia", icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQRQPA8Qi7lg9kj1shVj4E4uhH6lblZKa03WOSf0Hqm_XCuQyrd3-wROXjx4qG6bol4kfA&usqp=CAU")
        embed.set_footer(text=lang.DEFAULT_FOOTER.format(user=ctx.author), icon_url=ctx.author.avatar)

        select = discord.ui.Select(placeholder=lang.SEARCH_ON_WIKIPEDIA_PLACEHOLDER, options=[discord.SelectOption(label=proposition.title) for proposition in propositions])
        async def wiki_callback(interaction: discord.Interaction):
            nonlocal embed
            if interaction.user.id != ctx.author.id:
                raise NotInteractionOwner(ctx.author, interaction.user)
            
            page = wiki.get_page(select.values[0])
            embed.title = page.title
            url = (await page.urls())[0]
            embed.url = url
            summary = await page.summary()
            if summary == "": summary = lang.SEARCH_ON_WIKIPEDIA_EMPTY_SUMMARY.format(link=url) # TODO: Fetch the page text when the summary is empty
            embed.description = summary
            await wiki.close()
            await interaction.response.edit_message(embed=embed, view=None)
        async def do_or_raise(*args):
            try: await asyncio.wait_for(wiki_callback(*args), 5)
            except: raise ServiceUnavailableError
        select.callback = do_or_raise
        view = self.bot.add_bot(CustomView(select))
        await ctx.respond(embed=embed, view=view)