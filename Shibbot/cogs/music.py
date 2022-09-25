import discord
from discord.ext import commands

from bot import Shibbot


client = None


def setup(_client):
    global client
    client = _client
    client.add_cog(Music(client))


def plugin_is_enabled():
    async def predicate(ctx):
        if ctx.guild:
            async with client.aiodb() as db:
                async with db.execute(f"SELECT enabled FROM music_plugin WHERE guild_id=?", (ctx.guild.id,)) as cursor:
                    enabled = await cursor.fetchone()
            if enabled:
                enabled = enabled[0]
            return enabled
        else:
            return True
    return commands.check(predicate)


class Music(commands.Cog):
    def __init__(self, client):
        self.client: Shibbot = client

        self.client.cursor.execute(
            "CREATE TABLE IF NOT EXISTS music_plugin (guild_id INTEGER PRIMARY KEY, enabled BOOLEAN)")
        self.client.db.commit()
