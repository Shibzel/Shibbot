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
        # try:
        text = self.client.fl(await self.client.get_lang(ctx.guild)).ping
        embed_text = text["embed"]
        embed = discord.Embed(
            title=embed_text["title"],
            description=embed_text["description"].format(
                ping=round(self.client.latency*1000, 2),
                cpu=psutil.cpu_percent(),
                ram=psutil.virtual_memory()[2]
            ),
            color=discord.Color.dark_gold()
        )
        await ctx.reply(
            embed=embed,
            view=discord.ui.View(
                discord.ui.Button(
                    label=text["buttons"]["status"],
                    url="https://stats.uptimerobot.com/lmJ8oH1MgK"
                )
            )
        )
        # except:
        #     await ctx.send(f"It seems that I'm encountering problems, ping : {round(self.client.latency*1000, 2)}ms.\nStatus : https://stats.uptimerobot.com/lmJ8oH1MgK")
