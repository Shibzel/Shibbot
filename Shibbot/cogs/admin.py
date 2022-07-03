import asyncio

import orjson
import discord
from discord.ext import commands

import utils
from bot import Shibbot


def setup(client):
    client.add_cog(Admin(client))


class Admin(commands.Cog):
    def __init__(self, client):
        self.client: Shibbot = client

    @commands.command()
    async def dm_clear(self, ctx: commands.Context):
        messages = []
        async for message in ctx.channel.history(limit=None):
            if message.author == self.client.user:
                messages.append(message)
        tasks = [message.delete() for message in messages]
        await asyncio.gather(*tasks)
        await ctx.send("Done !")

    @commands.command()
    @commands.is_owner()
    async def owner(self, ctx):
        await ctx.reply(f"Hey <@!{self.client.owner_id}>, I know you ! You wrote my code !")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, plugin):
        try:
            self.client.reload_extension(f"cogs.{plugin}")
            await ctx.send(embed=CogEnabledEmbed(plugin, "reloaded"))
        except Exception as error:
            await ctx.send(embed=CogErrorEmbed(error))

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, plugin):
        try:
            self.client.load_extension(f"cogs.{plugin}")
            await ctx.send(embed=CogEnabledEmbed(plugin, "loaded"))
        except Exception as error:
            await ctx.send(embed=CogErrorEmbed(error))

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, plugin):
        try:
            self.client.unload_extension(f"cogs.{plugin}")
            await ctx.send(embed=CogEnabledEmbed(plugin, "unloaded"))
        except Exception as error:
            await ctx.send(embed=CogErrorEmbed(error))

    @commands.command()
    @commands.is_owner()
    async def showguilds(self, ctx: commands.Context):
        """Just a simple command that show guilds the bot is currently on."""
        list = []
        for guild in self.client.guilds:
            list.append(
                {
                    "name": guild.name,
                    "members": guild.member_count,
                    "created_at": guild.created_at
                }
            )
        path = "cache/guilds.json"
        utils.dump(
            list,
            path,
            option=orjson.OPT_INDENT_2
        )
        await ctx.send(
            content=f"Number total of guilds = {len(self.client.guilds)}",
            file=discord.File(path)
        )


class CogEnabledEmbed(discord.Embed):
    """Just a subclass of discord.Embed for when a cog loads."""

    def __init__(self, plugin, state):
        super().__init__(
            title="Admin",
            description=f"Cog `{plugin}` has been {state} successfully.",
            color=discord.Color.green())


class CogErrorEmbed(discord.Embed):
    """Subclass of discord.Embed for when a cog doesn't load and gets an error."""

    def __init__(self, error):
        super().__init__(
            title="Admin",
            description=f"An error has occurred :\n```{type(error)}: {error}```",
            color=discord.Color.red())
