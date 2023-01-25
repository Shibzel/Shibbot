import discord
from discord.ext import bridge, commands
from random import randint, shuffle, randint
from aiohttp import ClientSession
from orjson import loads
import re

from src.core import Shibbot
from src.models import PluginCog, EmbedViewer, CustomView
from src.utils import filter_doubles
from src.utils.json import json_from_urls
from src.errors import ServiceUnavailableError, MissingArgumentsError

from . import English, French


PLUGIN_NAME = "fun"

MEME_SUBREDDITS = ['memes', 'dankmemes', 'me_irl']

ER_REPLACE = re.compile(r"(\b\w{2,})er\b", re.IGNORECASE)
UWU = str.maketrans({"r": "w", "l": "w", "R": "W", "L": "W"})

class Fun(PluginCog):
    def __init__(self, bot):
        self.bot: Shibbot = bot
        super().__init__(
            plugin_name=PLUGIN_NAME,
            name={"en": "Fun", "fr": "Fun"},
            description={"en": "Entertainement", "fr": "Divertissement."},
            languages={"en": English, "fr": French}, emoji="🎉"
        )
        
    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        content = message.content
        if "(╯°□°)╯︵ ┻━┻" in content and not randint(0, 9):
            await message.reply("┬─┬ノ( º _ ºノ)")
        
    @bridge.bridge_command(name="meal", aliases=["dish"], description="Give a random dish that you could cook !")
    @commands.cooldown(1, 7, commands.BucketType.default)
    @commands.cooldown(1, 15, commands.BucketType.channel)
    async def get_meal(self, ctx: bridge.BridgeContext):
        async with ClientSession() as session:
            request = await session.get("https://www.themealdb.com/api/json/v1/1/random.php")
            if request.status != 200: raise ServiceUnavailableError()
            response = (await request.json(loads=loads))["meals"][0]
        
        use_reveal_button = False
        view = CustomView()
        embed = discord.Embed(title=response['strMeal'], url=response["strSource"], color=discord.Color.yellow())
        full_desc = response["strInstructions"]
        if len(full_desc) <= 256:
            desc = full_desc
        else:
            desc = full_desc[:256].replace("\n\n", "\n") + "..."
            use_reveal_button = True
        embed.add_field(name="Recipe", value=desc, inline=False)
        if youtube_url:= response["strYoutube"]:
            youtube_button = discord.ui.Button(label="Youtube video", url=youtube_url, emoji="🎥")
            view.add_item(youtube_button)
        ingredient_list = []
        for i in range(1, 20):
            measure, ingredient = response[f'strMeasure{i}'], response[f'strIngredient{i}']
            if measure in ("", " ") and ingredient in ("", " "):
                break
            ingredient_list.append(f"{measure}{f' {ingredient}'.title() if measure != '' else f'{ingredient}'}")
        if len(ingredient_list) > 3:
            ingredients = ", ".join(ingredient_list[:3]) + "..."
            use_reveal_button = True
        else:
            ingredients = "".join(f"- {ing}\n" for ing in ingredient_list)
        embed.add_field(name="Ingredients", value=ingredients)
        embed.add_field(name="Catergory", value=response["strCategory"])
        embed.add_field(name="Area/Country", value=response["strArea"])
        embed.set_image(url=response["strMealThumb"])
        embed.set_footer(icon_url=ctx.author.avatar, text=English.DEFAULT_FOOTER.format(user=ctx.author))
        if use_reveal_button:
            full_recipe_button = discord.ui.Button(label="Show full recipe", style=discord.ButtonStyle.green, emoji="⤵️")
            async def show_full_recipe(interaction: discord.Interaction):
                nonlocal embed
                embed.description = full_desc
                embed.fields.pop(0)
                embed.fields[0].value = "".join(f"- {ing}\n" for ing in ingredient_list)
                embed.set_thumbnail(url=embed.image.url)
                embed._image = None
                full_recipe_button.disabled = True
                await interaction.response.edit_message(embed=embed, view=view)
            full_recipe_button.callback = show_full_recipe
            view.add_item(full_recipe_button)
        
        await ctx.respond(embed=embed, view=view)
    
    async def _factory_memes(self, ctx, subreddit):
        url = "https://meme-api.com/gimme"
        number = 50
        async with ClientSession() as session:
            request = await session.get(url=f"{url}/{number}" if not subreddit else f"{url}/{subreddit}/{number}")
            if request.status != 200: raise ServiceUnavailableError()
            response = (await request.json(loads=loads))["memes"]
        
        lang = await self.get_lang(ctx)
        embeds = []
        author = ctx.author
        avatar = author.avatar.url
        nsfw = ctx.channel.is_nsfw()
        for meme in response:
            if meme["nsfw"] and not nsfw:
                continue
            embed = discord.Embed(title=meme["title"], url=meme["postLink"], color=0xff4500)
            embed.set_image(url=meme["url"])
            embed.set_footer(icon_url=avatar, text=lang.DEFAULT_FOOTER.format(user=author) + f" | 💖 {meme['ups']}")
            embeds.append(embed)
        
        next_button = discord.ui.Button(style=discord.ButtonStyle.blurple, label=lang.GET_MEME_NEXT_BUTTON)
        previous_button = discord.ui.Button(style=discord.ButtonStyle.gray, label=lang.GET_MEME_PREVIOUS_BUTTON)
        embed_viewer = EmbedViewer(embeds, next_button, previous_button, use_extremes=True, bot=self.bot)
        await embed_viewer.send_message(ctx)
    
    @discord.slash_command(name="memes", description="Memes from Reddit.", description_localizations={"fr": "Des memes provenant de Reddit."})
    @discord.option(name="subreddit", choices=MEME_SUBREDDITS, description="The meme subreddit.", description_localizations={"fr": "Le subreddit de memes."})
    @commands.cooldown(1, 15, commands.BucketType.default)
    async def slash_memes(self, ctx: discord.ApplicationContext, subreddit: str = None):
        await self._factory_memes(ctx, subreddit)
        
    @commands.command(name="memes", aliases=["meme"])
    @commands.cooldown(1, 15, commands.BucketType.default)
    async def prefixed_memes(self, ctx: commands.Context, subreddit: str = None):
        if subreddit not in (None, *MEME_SUBREDDITS):
            lang = await self.get_lang(ctx)
            raise MissingArgumentsError(ctx.command, lang.GET_MEME_CHECK_SUBREDDIT.format(subreds=", ".join(MEME_SUBREDDITS)))    
        
        await self._factory_memes(ctx, subreddit)          
        
    async def _image_factory(self, ctx: bridge.BridgeContext, urls: list[str], next_button_text: str, previous_button_text: str, footer: str):
        author = ctx.author
        avatar = author.avatar.url
        embeds = []
        for url in urls:
            embed = discord.Embed(color=discord.Color.dark_gold())
            embed.set_image(url=url)
            embed.set_footer(text=footer.format(user=author), icon_url=avatar)
            embeds.append(embed)
        
        next_button = discord.ui.Button(style=discord.ButtonStyle.blurple, label=next_button_text)
        previous_button = discord.ui.Button(style=discord.ButtonStyle.gray, label=previous_button_text)
        embed_viewer = EmbedViewer(embeds, next_button, previous_button, bot=self.bot)
        await embed_viewer.send_message(ctx)
        
    async def urbdict_factory(self, ctx, url):        
        async with ClientSession() as session:
            request = await session.get(url)
            if request.status != 200: raise ServiceUnavailableError()
            response = (await request.json(loads=loads))["list"]
        if response == []:
            raise commands.BadArgument()
        
        def clean_string(string: str):
            return string.replace("[", "**").replace("]", "**").replace("\n\n", "\n")
        embeds = []
        for definition in response:
            embed = discord.Embed(color=0x2faaee)
            embed.set_author(name="Urban Dictionary", url=definition["permalink"],
                             icon_url="https://slack-files2.s3-us-west-2.amazonaws.com/avatars/2018-01-11/297387706245_85899a44216ce1604c93_512.jpg")
            _def = clean_string(definition["definition"])
            example = clean_string(definition["example"])
            embed.add_field(name=f"Definition of \"{definition['word']}\" (by {definition['author']})", value=_def if len(_def) <= 1024 else _def[:1021]+"...", inline=False)
            embed.add_field(name="Example", value=example if len(example) <= 1024 else example[:1021]+"...", inline=False)
            embed.set_footer(icon_url=ctx.author.avatar, text=English.DEFAULT_FOOTER.format(user=ctx.author) + f" | 👍 {definition['thumbs_up']} • 👎 {definition['thumbs_down']}")
            embeds.append(embed)
        shuffle(embeds)
        
        next_button = discord.ui.Button(style=discord.ButtonStyle.blurple, label="Next Definition")
        previous_button = discord.ui.Button(style=discord.ButtonStyle.gray, label="Previous Definition")
        embed_viewer = EmbedViewer(embeds, next_button, previous_button, use_extremes=True)
        await embed_viewer.send_message(ctx)
    
    @bridge.bridge_group(aliases=["udict"])
    async def urbdict(self, *args): pass
        
    @urbdict.command(name="random", description="Gives the definition of a random definition on Urban Dictionary.")
    async def urbdict_random(self, ctx: bridge.BridgeContext):
        await self.urbdict_factory(ctx, url="https://api.urbandictionary.com/v0/random")
    
    @urbdict.command(name="search", description="Searches a definition of your word on Urban Dictionary.",
                           options=[discord.Option(required=True, name="word", description="The word you want the definition of.")])
    @commands.cooldown(1, 7, commands.BucketType.default)
    async def urbdict_search(self, ctx: bridge.BridgeContext, *, word: str = None):
        if not word:
            raise MissingArgumentsError(ctx.command)
        
        await self.urbdict_factory(ctx, url=f"https://api.urbandictionary.com/v0/define?term={word}")
        
    @bridge.bridge_command(name="shiba", aliases=["shibe", "shibes", "shibas"], description="Shows cute lil' pics of shibes.",
                           description_localizations={"fr": "Affiche de mignonnes petites photos de shibas."})
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def get_shibe_pictures(self, ctx: bridge.BridgeContext):
        urls = []
        for url_list in filter_doubles(await json_from_urls([f"https://shibe.online/api/shibes?count=100&urls=true&httpsUrls=true"]*2)):
            urls.extend(url_list)
        lang = await self.get_lang(ctx)
        await self._image_factory(ctx, urls, lang.GET_SHIBES_NEXT_BUTTON, lang.GET_SHIBES_PREVIOUS_BUTTON, lang.DEFAULT_FOOTER + " | shibe.online")
        
    @bridge.bridge_command(name="cat", aliases=["cats"], description="Shows cute lil' pics of cats.",
                           description_localizations={"fr": "Affiche de mignonnes petites photos de chat."})
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def get_cat_pictures(self, ctx: bridge.BridgeContext):
        urls = []
        for url_list in filter_doubles(await json_from_urls([f"https://shibe.online/api/cats?count=100&urls=true&httpsUrls=true"]*2)):
            urls.extend(url_list)
        lang = await self.get_lang(ctx)
        await self._image_factory(ctx, urls, lang.GET_CATS_NEXT_BUTTON, lang.GET_CATS_PREVIOUS_BUTTON, lang.DEFAULT_FOOTER + " | shibe.online")
    
    @bridge.bridge_command(name="bird", aliases=["birb", "birds"], description="Shows cute lil' pics of birb.",
                           description_localizations={"fr": "Affiche de mignonnes petites photos d'oiseau."})
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def get_birb_pictures(self, ctx: bridge.BridgeContext):
        urls = []
        for url_list in filter_doubles(await json_from_urls([f"https://shibe.online/api/birds?count=100&urls=true&httpsUrls=true"]*2)):
            urls.extend(url_list)
        lang = await self.get_lang(ctx)
        await self._image_factory(ctx, urls, lang.GET_BIRDS_NEXT_BUTTON, lang.GET_BIRDS_PREVIOUS_BUTTON, lang.DEFAULT_FOOTER + " | shibe.online")
        
    @bridge.bridge_command(name="capybara", aliases=["capy",], description="Shows cute lil' pics of capybaras.",
                           description_localizations={"fr": "Affiche de mignonnes petites photos de capybaras."})
    @commands.cooldown(1, 10, commands.BucketType.default)
    async def get_capy_pictures(self, ctx: bridge.BridgeContext):
        urls = []
        while len(urls) != 200:
            url = f"https://api.capy.lol/v1/capybara/{randint(1, 739)}" # https://github.com/Looskie/capybara-api/tree/main/capys
            if url not in urls: urls.append(self.get_lang(ctx))
        lang = await lang
        await self._image_factory(ctx, urls, lang.GET_CAPY_NEXT_BUTTON, lang.GET_CAPY_PREVIOUS_BUTTON, lang.DEFAULT_FOOTER + " | capy.lol")
    
    @commands.command(name="ratio", description="fatherless + L + stay mad")
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def _ratio(self, ctx: commands.Context):
        await ctx.message.delete()
        words = ["ratio", "nobody asked", "fatherless", "maidenless", "no bitches", "don't care", "L", "ur bad", "poor", "skill issue", "ew",
                    "motherless", "orphan", "friendless", "lifeless", "you're the reason your dad left", "cry about it", "stay mad lmao"]
        shuffle(words)
        text = " + ".join(words[:randint(3, 5)])
        if ctx.message.reference:
            reply_message = ctx.channel.get_partial_message(ctx.message.reference.message_id)
            return await reply_message.reply(text)
        await ctx.send(text)
        
    @bridge.bridge_command(name="uwuify", aliases=["uwu"], description="Uwuifies a given text.", description_localizations={"fr": "Uwuifie un texte qui a été donné."},
                           options=[discord.Option(name="text", description="The text to uwuify.", description_localizations={"fr": "Le texte à uwuifier."})])
    @commands.cooldown(1, 7, commands.BucketType.channel)
    async def _uwu(self, ctx: bridge.BridgeContext, *, text: str = None):
        if not text:
            raise MissingArgumentsError(ctx.command)
        
        text = ER_REPLACE.sub(r"\g<1>a", text).translate(UWU)
        result = []
        for index, word in enumerate(text.split(" ")):
            if index % 4 == 0: result.append(f"{word[0]}-{word[0]}{word[1:]}")
            else: result.append(word)

        await ctx.respond(" ".join(result))
        
    # @bridge.bridge_command(name="button", description="Just a button, nothing dangerous.", description_localizations={"fr": "Juste un bouton, rien de dangereux."})
    # @commands.cooldown(1, 180, commands.BucketType.channel)
    # async def funni_button(self, ctx: bridge.BridgeContext):
    #     lang = await self.get_lang(ctx)
        
    #     actions_list = []
    #     def action(foo): actions_list.append(foo)
    #     @action
    #     async def message(interaction): await reply_method(choice(lang.FUNNI_BUTTON_MESSAGES).format(user=interaction.user.mention))
    #     @action
    #     async def ephemeral_message(interaction): await reply_method(choice(lang.FUNNI_BUTTON_EPHEMERAL_MESSAGES), ephemeral=True)
    #     @action
    #     async def chonk_shibe(interaction):
    #         smol_to_chonk_shibes = [
    #             "",
    #             "",
    #         ]
    #         embeds = []
    #         for shibe in smol_to_chonk_shibes:
    #             embed = discord.Embed(color=discord.Color.dark_gold())
    #             embed.set_image(url=shibe)
    #         next_button = discord.ui.Button(style=discord.ButtonStyle.danger, label=lang.FUNNI_BUTTON_BIGGER_SHIBE_BUTTON)
    #         previous_button = discord.ui.Button(style=discord.ButtonStyle.blurple, label=lang.FUNNI_BUTTON_smoller_SHIBE_BUTTON)
    #         embed_viewer = EmbedViewer(embeds, next_button, previous_button, bot=self.bot)
    #         embed_viewer.next_button.disabled = False
    #         embed_viewer.previous_button.disabled = False
    #         embed_viewer.page = int(len(smol_to_chonk_shibes)/2)
    #         await reply_method(embed=embeds[embed_viewer.page], view=embed_viewer)
    #     # @action
    #     # async def shrek_script(interaction):
    #     #     if (not ctx.guild or interaction.user.guild_permissions.administrator()) and not randint(0, 99): # Very low chances of happening
    #     #         async for chunk in get_local_data("/fun/funni_button/shrek.json"):
    #     #             await reply_method(chunk)    
    #     #     else:
    #     #         await the_button_callback(interaction)
    #     @action
    #     async def gif_or_images(interaction):
    #         links = [
    #             "",
    #             "",
    #         ]
    #         await reply_method(choice(links), delete_after=5)
    #     @action
    #     async def kick(interaction):
    #         if not randint(0, 99) and ctx.guild:
    #             try: 
    #                 return await ctx.guild.kick(interaction.user)
    #             except: pass
    #         await the_button_callback(interaction)
    #     @action
    #     async def another_button(interaction): await reply_method(view=CustomView(the_button, timeout=300))
        
    #     the_button = discord.ui.Button(style=discord.ButtonStyle.danger, label=lang.FUNNI_BUTTON_BUTTON_NAME)
    #     async def the_button_callback(interaction: discord.Interaction):
    #         action = choice(actions_list)
    #         await action(interaction)
    #     the_button.callback = the_button_callback
            
    #     response_message = await ctx.respond(view=CustomView(the_button, timeout=300))
    #     if isinstance(response_message, discord.Message):
    #         reply_method = response_message.reply
    #     elif isinstance(response_message, discord.Interaction):
    #         reply_method = response_message.message.reply