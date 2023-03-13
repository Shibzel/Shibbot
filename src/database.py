"""All core database functions."""
import sqlite3
import aiosqlite
import discord
from discord.ext import commands, bridge
import os
import asyncio

from src.constants import DEFAULT_PREFIX, DEFAULT_LANGUAGE, DATABASE_FILE_PATH
from src.logging import Logger


logger = Logger(__name__)

if not os.path.exists(DATABASE_FILE_PATH):
    open(DATABASE_FILE_PATH, "x")
    logger.warn(f"Missing {DATABASE_FILE_PATH} file, creating one.")


def db() -> sqlite3.Connection:
    return sqlite3.connect(DATABASE_FILE_PATH)


def aiodb() -> aiosqlite.Connection:
    return aiosqlite.connect(DATABASE_FILE_PATH)


IsOrHasGuild = discord.Guild | commands.Context | bridge.BridgeContext


def _is_or_has_guild(obj: IsOrHasGuild):
    return obj if isinstance(obj, discord.Guild) else getattr(obj, "guild", None)


async def get_language(obj: IsOrHasGuild):
    """Returns the language code of an user/guild."""
    async with AsyncDB() as db:
        return await db.get_language(_is_or_has_guild(obj))


async def get_prefix(obj: IsOrHasGuild):
    """Returns the prefix of a guild."""
    async with AsyncDB() as db:
        return await db.get_prefix(_is_or_has_guild(obj))


class AsyncDB:
    def __init__(self, path: str = None, commit_on_exit: bool = False):
        self.commit_on_exit = commit_on_exit
        self._conn = aiodb() if not path else aiosqlite.connect(path)
        self._connection = None

    @property
    def conn(self):
        if not self._connection:
            raise RuntimeError(
                f"coroutine '{type(self).__name__}' was never awaited")
        return self._connection

    async def connect(self):
        self._connection = await self._conn
        return self

    def __await__(self) -> "AsyncDB":
        return self.connect().__await__()

    async def __aenter__(self) -> "AsyncDB":
        return await self

    async def __aexit__(self, *args) -> None:
        await self.close()

    async def commit(self):
        await self.conn.commit()

    async def close(self):
        if self.commit_on_exit:
            await self.commit()
        await self.conn.close()

    async def create_or_fetch_guild(self, bot, guild: discord.Guild):
        """Fetch the infos of a guild inside the guild table or insert it."""
        async with self.conn.execute(f"SELECT * FROM guilds WHERE guild_id=?", (guild.id,)) as cursor:
            if data := await cursor.fetchone():
                return data
        # Tries to sync the bot's language with the server's one
        language = guild.preferred_locale if guild.preferred_locale in bot.languages else DEFAULT_LANGUAGE
        data = (guild.id, DEFAULT_PREFIX, language,)
        cursor = await self.conn.execute("INSERT INTO guilds (guild_id, prefix, lang) VALUES (?,?,?)", data)
        await cursor.close()

    async def get_prefix(self, guild: discord.Guild):
        """Gets the prefix."""
        try:
            if guild:
                async with self.conn.execute("SELECT prefix FROM guilds WHERE guild_id=?", (guild.id,)) as cursor:
                    if prefix := await cursor.fetchone():
                        return prefix[0]
        except Exception as e:
            logger.error(f"Failed getting prefix on guild '{guild}'.", e)
        return DEFAULT_PREFIX

    async def change_prefix(self, bot, guild: discord.Guild, prefix: str):
        await self.create_or_fetch_guild(bot, guild)
        cursor = await self.conn.execute("UPDATE guilds SET prefix=? WHERE guild_id=?", (prefix, guild.id,))
        await cursor.close()

    async def get_language(self, guild: discord.Guild):
        """Gets the language of a guild."""
        try:
            if guild:
                async with self.conn.execute("SELECT lang FROM guilds WHERE guild_id=?", (guild.id,)) as cursor:
                    if lang := await cursor.fetchone():
                        return lang[0]
        except Exception as e:
            logger.error(f"Failed getting language on guild '{guild}'.", e)
        return DEFAULT_LANGUAGE

    async def change_language(self, bot, guild: discord.Guild, language: str):
        await self.create_or_fetch_guild(bot, guild)
        cursor = await self.conn.execute("UPDATE guilds SET lang=? WHERE guild_id=?", (language, guild.id,))
        await cursor.close()

    async def plugin_is_enabled(self, guild: discord.Guild, plugin: str, guild_only: bool = False):
        if not guild:
            return not guild_only
        async with self.conn.execute(f"SELECT enabled FROM {plugin}_plugin WHERE guild_id=?", (guild.id,)) as cursor:
            if enabled := await cursor.fetchone():
                enabled = enabled[0]
            return enabled

    async def enable_plugin(self, guild: discord.Guild, plugin: str, enable: bool = True):
        await self.bulk_enable_plugin(guild, {plugin: enable})

    async def bulk_enable_plugin(self, guild: discord.Guild, mapping: dict[str, bool]):
        async def _enable_plugin(plugin, enable):
            async with self.conn.execute(f"SELECT * FROM {plugin}_plugin WHERE guild_id=?", (guild.id,)) as cursor:
                args = (f"UPDATE {plugin}_plugin SET enabled=? WHERE guild_id=?", (enable, guild.id,)) if await cursor.fetchone(
                ) else (f"INSERT INTO {plugin}_plugin (guild_id, enabled) VALUES (?,?)", (guild.id, enable,))
                cursor = await cursor.execute(*args)
                await cursor.close()
        await asyncio.gather(*[_enable_plugin(name, int(bool(enabled))) for name, enabled in mapping.items()])
