import discord
from discord.ext import commands, tasks

import utils
from bot import Shibbot

client = None


def setup(_client):
    global client
    client = _client
    client.add_cog(Fun(client))


def plugin_is_enabled():
    async def predicate(ctx):
        if ctx.guild:
            client.cursor.execute(
                f"SELECT enabled FROM fun_plugin WHERE guild_id=?",
                (ctx.guild.id,)
            )
            enabled = client.cursor.fetchone()
            if enabled:
                enabled = enabled[0]
            return enabled
        else:
            return True
    return commands.check(predicate)


class Fun(commands.Cog):
    def __init__(self, client):
        self.client: Shibbot = client
        self.reddit: utils.Reddit = self.client.reddit

        self.client.cursor.execute(
            "CREATE TABLE IF NOT EXISTS fun_plugin (guild_id INTEGER PRIMARY KEY, enabled BOOLEAN)")
