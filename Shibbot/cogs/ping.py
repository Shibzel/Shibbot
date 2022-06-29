import psutil
import discord
from discord.ext import commands

from bot import Shibbot


def setup(client):
    client.add_cog(Ping(client))


class Ping(commands.Cog):
    def __init__(self, client):
        self.client: Shibbot = client

    @commands.command()
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def ping(self, ctx: commands.Context):
        """Checks if the bot is alive."""
        text = self.client.fl(await self.client.get_lang(ctx.guild)).ping["embed"]
        await ctx.reply(
            embed=discord.Embed(
                title=text["title"],
                description=text["description"].format(
                    ping=round(self.client.latency*1000, 2),
                    cpu=psutil.cpu_percent(),
                    ram=psutil.virtual_memory()[2]
                ),
                color=discord.Color.dark_gold()
            )
        )
