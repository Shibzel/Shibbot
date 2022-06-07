import aiohttp
import discord
from discord.ext import commands

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
