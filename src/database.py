"""All core database functions."""
import sqlite3
import aiosqlite
import discord
from discord.ext import commands, bridge
from functools import partial

from src.constants import DEFAULT_PREFIX, DEFAULT_LANGUAGE


__all__ = ("GUILD_TABLE_NAME", "PLUGINS_TABLE_NAME", "IsOrHasGuild", "is_or_has_guild", "AsyncDB")

GUILD_TABLE_NAME = "guild"
PLUGINS_TABLE_NAME = "plugins"

IsOrHasGuild = discord.Guild | commands.Context | bridge.BridgeContext

def is_or_has_guild(obj: IsOrHasGuild):
    return obj if isinstance(obj, discord.Guild) else getattr(obj, "guild", None)

class AsyncDB(aiosqlite.Connection):
    def __init__(
            self,
            path: str,
            commit_on_exit: bool = True,
            iter_chunk_size: int = 64
        ):
        self.commit_on_exit = commit_on_exit
        self.path = path
        super().__init__(
            partial(sqlite3.connect, self.path),
            iter_chunk_size=iter_chunk_size
        )
        
    async def __aenter__(self) -> "AsyncDB":
        return self
    
    async def __aexit__(self, *args) -> None:
        await self.commit()

    async def close(self):
        if self.commit_on_exit:
            await self.commit()
        await super().close()

    async def create_or_fetch_guild(self, bot, guild: discord.Guild):
        """Fetch the infos of a guild inside the guild table or insert it."""
        query = f"SELECT * FROM guilds WHERE guild_id=?"
        async with self.execute(query, (guild.id,)) as cursor:
            if data := await cursor.fetchone():
                return data
        # Tries to sync the bot's language with the server's one
        language = (guild.preferred_locale 
            if guild.preferred_locale in bot.languages else DEFAULT_LANGUAGE)
        data = (guild.id, DEFAULT_PREFIX, language,)
        query = "INSERT INTO guilds (guild_id, prefix, lang) VALUES (?, ?, ?)"
        await self.execute(query, data)

    async def get_prefix(self, guild: discord.Guild):
        """Gets the prefix."""
        try:
            if guild:
                query = "SELECT prefix FROM guilds WHERE guild_id=?"
                async with self.execute(query, (guild.id,)) as cursor:
                    if prefix := await cursor.fetchone():
                        return prefix[0]
        except Exception as e:
            pass
        return DEFAULT_PREFIX

    async def change_prefix(self, bot, guild: discord.Guild, prefix: str):
        await self.create_or_fetch_guild(bot, guild)
        query = "UPDATE guilds SET prefix=? WHERE guild_id=?"
        await self.execute(query, (prefix, guild.id,))

    async def get_language(self, guild: discord.Guild):
        """Gets the language of a guild."""
        try:
            if guild:
                query = "SELECT lang FROM guilds WHERE guild_id=?"
                async with self.execute(query, (guild.id,)) as cursor:
                    if lang := await cursor.fetchone():
                        return lang[0]
        except Exception as e:
            pass
        return DEFAULT_LANGUAGE

    async def change_language(self, bot, guild: discord.Guild, language: str):
        await self.create_or_fetch_guild(bot, guild)
        query = "UPDATE guilds SET lang=? WHERE guild_id=?"
        await self.execute(query, (language, guild.id,))

    async def plugin_is_enabled(self, guild: discord.Guild, plugin: str, 
                                guild_only: bool = False):
        if not guild:
            return not guild_only
        query = f"SELECT {plugin} FROM {PLUGINS_TABLE_NAME} WHERE guild_id=?"
        async with self.execute(query, (guild.id,)) as cursor:
            if enabled := await cursor.fetchone():
                enabled = enabled[0]
            return enabled

    async def enable_plugin(self, guild: discord.Guild, plugin: str, enable: bool = True):
        await self.bulk_enable_plugin(guild, {plugin: enable})

    async def bulk_enable_plugin(self, guild: discord.Guild, mapping: dict[str, bool]):
        query = f"SELECT * FROM {PLUGINS_TABLE_NAME} WHERE guild_id=?"
        async with self.execute(query, (guild.id,)) as cursor:
            if await cursor.fetchone():
                query = f"""
                UPDATE {PLUGINS_TABLE_NAME}
                SET {', '.join(f'{k}=?' for k in mapping.keys())}
                WHERE guild_id=?"""
                await cursor.execute(query, (*mapping.values(), guild.id))
            else:
                query = f"""
                INSERT INTO {PLUGINS_TABLE_NAME} (
                    guild_id,
                    {', '.join(mapping.keys())}
                )
                VALUES (? ,{', '.join('?' for _ in range(len(mapping)))})"""
                await cursor.execute(query, (guild.id, *mapping.values()))
