import aiohttp
import discord
from discord.ext import commands
import aiolibretrans

from utils import remove_chars, EmbedViewer
from bot import Shibbot


client = None


def setup(_client):
    global client
    client = _client
    client.add_cog(Tools(client))


def plugin_is_enabled():
    async def predicate(ctx):
        if ctx.guild:
            async with client.aiodb() as db:
                async with db.execute(
                    f"SELECT enabled FROM tools_plugin WHERE guild_id=?",
                    (ctx.guild.id,)
                ) as cursor:
                    enabled = await cursor.fetchone()
            if enabled:
                enabled = enabled[0]
            return enabled
        else:
            return True
    return commands.check(predicate)


class Tools(commands.Cog):
    def __init__(self, client):
        self.client: Shibbot = client

        self.client.cursor.execute(
            "CREATE TABLE IF NOT EXISTS tools_plugin (guild_id INTEGER PRIMARY KEY, enabled BOOLEAN)")

    @commands.command(name="translate", aliases=["trans"])
    @plugin_is_enabled()
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def translate_text(self, ctx: commands.Context, language=None, *, sentence=None):
        lang = self.client.fl(await self.client.get_lang(ctx))
        text = lang.translate_text
        if not language or not sentence:
            embed_text = text["checks"]["missing_args"]
            return await ctx.reply(
                embed=discord.Embed(
                    description="( ﾉ ﾟｰﾟ)ﾉ "+embed_text["description"],
                    color=discord.Color.dark_gold()
                )
            )

        async with aiolibretrans.LibreTranslate(target=language) as translator:
            try:
                result = await translator.translate(text=sentence)
            except aiolibretrans.BadRequest:
                embed_text = text["checks"]["bad_args"]
                return await ctx.reply(
                    embed=discord.Embed(
                        title=embed_text["title"],
                        description="(#_<-) "+embed_text["description"],
                        color=discord.Color.red()
                    )
                )
            except aiolibretrans.RequestError:
                pass  # Service not available

        embed = discord.Embed(color=0x4b8cf5)
        embed.set_author(
            name="Translator", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Google_Translate_logo.svg/800px-Google_Translate_logo.svg.png")
        embed.add_field(name="Original text :", value=sentence)
        embed.add_field(name="Translated :", value=result)
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="urbandict", aliases=["udict"])
    @plugin_is_enabled()
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def urbain_dictionary(self, ctx: commands.Context, *, keywords: str = None):
        lang = self.client.fl(await self.client.get_lang(ctx))
        text = lang.urbain_dictionary

        def clean_string(string):
            return remove_chars(string, "][").replace("\n\n", "\n")

        if not keywords:
            embed_text = text["checks"]["missing_args"]
            return await ctx.reply(
                embed=discord.Embed(
                    description="( ﾉ ﾟｰﾟ)ﾉ "+embed_text["description"],
                    color=discord.Color.dark_gold()
                )
            )

        async with aiohttp.ClientSession(
            headers={
                "X-RapidAPI-Host": "mashape-community-urban-dictionary.p.rapidapi.com",
                "X-RapidAPI-Key": self.client.config["rapidapi"]
            }
        ) as session:
            results = await session.get(
                "https://mashape-community-urban-dictionary.p.rapidapi.com/define",
                params={"term": keywords}
            )
            try:
                json_results = (await results.json())["list"]
            except:
                raise commands.BadArgument

        fields_text = text["embed"]["fields"]

        def generate_embed(definition):
            embed = discord.Embed(color=0x2faaee)
            embed.set_author(
                name="Urban Dictionary",
                icon_url="https://slack-files2.s3-us-west-2.amazonaws.com/avatars/2018-01-11/297387706245_85899a44216ce1604c93_512.jpg",
                url=definition["permalink"]
            )

            word_definition = clean_string(definition["definition"])
            example = clean_string(definition["example"])
            embed.add_field(
                name=fields_text[0]["name"].format(
                    word=definition["word"],
                    author=definition["author"],
                ),
                value=word_definition if len(
                    word_definition) < 400 else word_definition[:400]+"..."
            )
            embed.add_field(
                name=fields_text[1]["name"], value=example if len(
                    example) < 400 else example[:400]+"..."
            )
            embed.set_footer(
                text=lang.DEFAULT_REQUESTED_FOOTER.format(author=ctx.author),
                icon_url=ctx.author.avatar if ctx.author.avatar else None)
            return embed

        button_text = text["buttons"]
        next_button = discord.ui.Button(
            style=discord.ButtonStyle.green,
            label=button_text["next"])
        previous_button = discord.ui.Button(
            style=discord.ButtonStyle.gray,
            label=button_text["previous"])

        embed_viewer = EmbedViewer(
            ctx,
            json_results,
            generate_embed,
            next_button,
            previous_button
        )

        await ctx.reply(
            embed=embed_viewer.get_first_page(),
            view=embed_viewer
        )

    @commands.command(name="covid")
    @plugin_is_enabled()
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def get_covid_stats(self, ctx: commands.Context, country: str = None):
        def codify(value):
            return f"`{'n/a' if value == 0 else value}`"
        lang = self.client.fl(await self.client.get_lang(ctx))
        text = lang.get_covid_stats
        if not country:
            embed_text = text["checks"]["missing_args"]
            return await ctx.reply(
                embed=discord.Embed(
                    description="( ﾉ ﾟｰﾟ)ﾉ "+embed_text["description"],
                    color=discord.Color.dark_gold()
                )
            )

        embed_text = text["loading_embed"]
        message = await ctx.reply(
            embed=discord.Embed(
                title=embed_text["title"],
                description=embed_text["description"],
                color=discord.Color.dark_red()
            )
        )
        async with aiohttp.ClientSession() as session:
            stats = await session.get(f"https://coronavirus-19-api.herokuapp.com/countries/{country}")
            try:
                json_stats = await stats.json()
            except Exception:
                await message.delete()
                raise commands.BadArgument
        embed_text = text["embed"]
        embed = discord.Embed(
            description=embed_text["description"],
            color=discord.Color.dark_red()
        )
        embed.set_author(
            name=embed_text["title"].format(country=country.upper()),
            icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT6U1D1hdMlpJkyFQ2MAIhzNQe3K7ovo3fN2g&usqp=CAU"
        )
        fields_text = embed_text["fields"]
        embed.add_field(name=fields_text[0]["name"],
                        value=codify(json_stats["cases"]))
        embed.add_field(name=fields_text[1]["name"],
                        value=codify(json_stats["todayCases"]))
        embed.add_field(name=fields_text[2]["name"],
                        value=codify(json_stats["deaths"]))
        embed.add_field(name=fields_text[3]["name"],
                        value=codify(json_stats["todayDeaths"]))
        embed.add_field(name=fields_text[4]["name"],
                        value=codify(json_stats["recovered"]))
        embed.add_field(name=fields_text[5]["name"],
                        value=codify(json_stats["active"]))
        embed.add_field(name=fields_text[6]["name"],
                        value=codify(json_stats["critical"]))
        embed.add_field(name=fields_text[7]["name"],
                        value=codify(json_stats["casesPerOneMillion"]))
        embed.add_field(name=fields_text[8]["name"],
                        value=codify(json_stats["deathsPerOneMillion"]))
        embed.add_field(name=fields_text[9]["name"],
                        value=codify(json_stats["totalTests"]))
        embed.add_field(name=fields_text[10]["name"],
                        value=codify(json_stats["testsPerOneMillion"]))
        embed.add_field(name=fields_text[11]["name"],
                        value=fields_text[11]["value"])
        embed.set_footer(
            text=lang.DEFAULT_REQUESTED_FOOTER.format(author=ctx.author),
            icon_url=ctx.author.avatar
        )
        await message.edit(embed=embed)
