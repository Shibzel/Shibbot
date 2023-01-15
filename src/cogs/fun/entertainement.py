import discord
from discord.ext import bridge, commands
from random import randint, shuffle, randint
from aiohttp import ClientSession
from orjson import loads

from src import __version__ as version
from src.core import Shibbot
from src.models import PluginCog, EmbedViewer, CustomView
from src.utils import filter_doubles
from src.utils.json import json_from_urls
from src.errors import ServiceUnavailableError

from . import English, French


PLUGIN_NAME = "fun"
HEADERS = {'User-Agent': f'Shibbot/{version} (+https://github.com/Shibzel/Shibbot)'}

class Fun(PluginCog):
    def __init__(self, bot):
        self.bot: Shibbot = bot
        super().__init__(
            plugin_name=PLUGIN_NAME,
            name={"en": "Fun", "fr": "Fun"},
            description={"en": "Entertainement", "fr": "Divertissement."},
            languages={"en": English, "fr": French}, emoji="🎉"
        )
        
    @bridge.bridge_command(name="meal", aliases=["dish"], description="Give a random dish that you could cook !")
    @commands.cooldown(1, 7, commands.BucketType.default)
    @commands.cooldown(1, 15, commands.BucketType.channel)
    async def get_meal(self, ctx: bridge.BridgeApplicationContext):
        async with ClientSession(headers=HEADERS) as session:
            request = await session.get("https://www.themealdb.com/api/json/v1/1/random.php")
            if request.status != 200: raise ServiceUnavailableError()
            response = (await request.json(loads=loads))["meals"][0]
        
        view = CustomView()
        embed = discord.Embed(title=response['strMeal'], url=response["strSource"])
        full_desc = response["strInstructions"]
        if len(full_desc) <= 512:
            desc = full_desc
        else:
            desc = full_desc[:499] + "..."
            full_recipe_button = discord.ui.Button(label="Show full recipe", style=discord.ButtonStyle.green, emoji="⤵️")
            async def show_full_recipe(interaction: discord.Interaction):
                nonlocal embed
                embed.description = full_desc
                for field in embed.fields:
                    if field.name == "Recipe":
                        embed.fields.remove(field)
                        break
                full_recipe_button.disabled = True
                await interaction.response.edit_message(embed=embed, view=view)
            full_recipe_button.callback = show_full_recipe
            view.add_item(full_recipe_button)
        embed.add_field(name="Recipe", value=desc, inline=False)
        if youtube_url:= response["strYoutube"]:
            youtube_button = discord.ui.Button(label="Youtube video", url=youtube_url, emoji="🎥")
            view.add_item(youtube_button)
        ingredients = ""
        for i in range(1, 20):
            if response[f"strIngredient{i}"] == "":
                break
            ingredients += f"- {response[f'strMeasure{i}']} {response[f'strIngredient{i}']}\n"
        embed.add_field(name="Ingredients", value=ingredients)
        embed.add_field(name="Catergory", value=response["strCategory"])
        embed.add_field(name="Area/Country", value=response["strArea"])
        if tags:= response["strTags"]:
            embed.add_field(name="Tag(s)", value=", ".join(tag.title() for tag in tags.split(",")))
        embed.set_thumbnail(url=response["strMealThumb"])
        embed.set_footer(icon_url=ctx.author.avatar, text=English.DEFAULT_FOOTER.format(user=ctx.author))
        
        await ctx.respond(embed=embed, view=view)
        
    async def _image_factory(self, ctx: bridge.BridgeApplicationContext, urls: list[str], next_button_text: str, previous_button_text: str, footer: str):
        next_button = discord.ui.Button(style=discord.ButtonStyle.blurple, label=next_button_text)
        previous_button = discord.ui.Button(style=discord.ButtonStyle.gray, label=previous_button_text)
        
        author = ctx.author
        avatar = author.avatar.url
        embeds = []
        for url in urls:
            embed = discord.Embed(color=discord.Color.dark_gold())
            embed.set_image(url=url)
            embed.set_footer(text=footer.format(user=author), icon_url=avatar)
            embeds.append(embed)
        
        embed_viewer = EmbedViewer(embeds, next_button, previous_button, bot=self.bot)
        await embed_viewer.send_message(ctx)
        
    @bridge.bridge_command(name="shiba", aliases=["shibe", "shibes", "shibas"], description="Shows cute lil' pics of shibes.",
                           description_localizations={"fr": "Affiche de mignonnes petites photos de shibas."})
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def get_shibe_pictures(self, ctx: bridge.BridgeApplicationContext):
        lang = self.bot.loop.create_task(self.get_lang(ctx))
        urls = []
        for url_list in filter_doubles(await json_from_urls([f"https://shibe.online/api/shibes?count=100&urls=true&httpsUrls=true"]*2, headers=HEADERS)):
            urls.extend(url_list)
        lang = await lang
        await self._image_factory(ctx, urls, lang.GET_SHIBES_NEXT_BUTTON, lang.GET_SHIBES_PREVIOUS_BUTTON, lang.DEFAULT_FOOTER + " | shibe.online")
        
    @bridge.bridge_command(name="cat", aliases=["cats"], description="Shows cute lil' pics of cats.",
                           description_localizations={"fr": "Affiche de mignonnes petites photos de chat."})
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def get_cat_pictures(self, ctx: bridge.BridgeApplicationContext):
        lang = self.bot.loop.create_task(self.get_lang(ctx))
        urls = []
        for url_list in filter_doubles(await json_from_urls([f"https://shibe.online/api/cats?count=100&urls=true&httpsUrls=true"]*2, headers=HEADERS)):
            urls.extend(url_list)
        lang = await lang
        await self._image_factory(ctx, urls, lang.GET_CATS_NEXT_BUTTON, lang.GET_CATS_PREVIOUS_BUTTON, lang.DEFAULT_FOOTER + " | shibe.online")
    
    @bridge.bridge_command(name="bird", aliases=["birb", "birds"], description="Shows cute lil' pics of birb.",
                           description_localizations={"fr": "Affiche de mignonnes petites photos d'oiseau."})
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def get_birb_pictures(self, ctx: bridge.BridgeApplicationContext):
        lang = self.bot.loop.create_task(self.get_lang(ctx))
        urls = []
        for url_list in filter_doubles(await json_from_urls([f"https://shibe.online/api/birds?count=100&urls=true&httpsUrls=true"]*2, headers=HEADERS)):
            urls.extend(url_list)
        lang = await lang
        await self._image_factory(ctx, urls, lang.GET_BIRDS_NEXT_BUTTON, lang.GET_BIRDS_PREVIOUS_BUTTON, lang.DEFAULT_FOOTER + " | shibe.online")
        
    @bridge.bridge_command(name="capybara", aliases=["capy",], description="Shows cute lil' pics of capybaras.",
                           description_localizations={"fr": "Affiche de mignonnes petites photos de capybaras."})
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def get_capy_pictures(self, ctx: bridge.BridgeApplicationContext):
        lang = self.bot.loop.create_task(self.get_lang(ctx))
        urls = []
        while len(urls) != 200:
            url = f"https://api.capy.lol/v1/capybara/{randint(1, 739)}" # https://github.com/Looskie/capybara-api/tree/main/capys
            if url not in urls: urls.append(url)
        lang = await lang
        await self._image_factory(ctx, urls, lang.GET_CAPY_NEXT_BUTTON, lang.GET_CAPY_PREVIOUS_BUTTON, lang.DEFAULT_FOOTER + " | capy.lol")
    
    @commands.command(name="ratio", description="fatherless + L + stay mad")
    @commands.cooldown(1, 7, commands.BucketType.channel)
    async def _ratio(self, ctx: commands.Context):
        await ctx.message.delete()
        words = ["ratio", "nobody asked", "fatherless", "maidenless",
                 "no bitches", "don't care", "L", "ur bad", "poor",
                 "skill issue", "ew", "motherless", "orphan", "friendless",
                 "lifeless", "you're the reason your dad left", "cry about it",
                 "stay mad", "adios", ]
        shuffle(words)
        shuffled_words = words[:randint(3, 5)]
        text = " + ".join(shuffled_words)
        if ctx.message.reference:
            reply_message = ctx.channel.get_partial_message(ctx.message.reference.message_id)
            return await reply_message.reply(text)
        await ctx.send(text)