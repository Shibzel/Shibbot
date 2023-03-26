"""All core database functions."""
import aiosqlite
import discord
from discord.ext import commands, bridge
import os

from src.constants import DEFAULT_PREFIX, DEFAULT_LANGUAGE, DATABASE_FILE_PATH
from src.logging import Logger


logger = Logger(__name__)

GUILD_TABLE_NAME = "guild"
PLUGINS_TABLE_NAME = "plugins"
IsOrHasGuild = discord.Guild | commands.Context | bridge.BridgeContext


if not os.path.exists(DATABASE_FILE_PATH):
    open(DATABASE_FILE_PATH, "x")
    logger.warn(f"Missing {DATABASE_FILE_PATH} file, creating one.")


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
        self._conn = aiosqlite.connect(path or DATABASE_FILE_PATH)
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
        query = f"SELECT * FROM guilds WHERE guild_id=?"
        async with self.conn.execute(query, (guild.id,)) as cursor:
            if data := await cursor.fetchone():
                return data
        # Tries to sync the bot's language with the server's one
        language = (guild.preferred_locale 
            if guild.preferred_locale in bot.languages else DEFAULT_LANGUAGE)
        data = (guild.id, DEFAULT_PREFIX, language,)
        query = "INSERT INTO guilds (guild_id, prefix, lang) VALUES (?,?,?)"
        await self.conn.execute(query, data)

    async def get_prefix(self, guild: discord.Guild):
        """Gets the prefix."""
        try:
            if guild:
                query = "SELECT prefix FROM guilds WHERE guild_id=?"
                async with self.conn.execute(query, (guild.id,)) as cursor:
                    if prefix := await cursor.fetchone():
                        return prefix[0]
        except Exception as e:
            logger.error(f"Failed getting prefix on guild '{guild}'.", e)
        return DEFAULT_PREFIX

    async def change_prefix(self, bot, guild: discord.Guild, prefix: str):
        await self.create_or_fetch_guild(bot, guild)
        query = "UPDATE guilds SET prefix=? WHERE guild_id=?"
        await self.conn.execute(query, (prefix, guild.id,))

    async def get_language(self, guild: discord.Guild):
        """Gets the language of a guild."""
        try:
            if guild:
                query = "SELECT lang FROM guilds WHERE guild_id=?"
                async with self.conn.execute(query, (guild.id,)) as cursor:
                    if lang := await cursor.fetchone():
                        return lang[0]
        except Exception as e:
            logger.error(f"Failed getting language on guild '{guild}'.", e)
        return DEFAULT_LANGUAGE

    async def change_language(self, bot, guild: discord.Guild, language: str):
        await self.create_or_fetch_guild(bot, guild)
        query = "UPDATE guilds SET lang=? WHERE guild_id=?"
        await self.conn.execute(query, (language, guild.id,))

    async def plugin_is_enabled(self, guild: discord.Guild, plugin: str, 
                                guild_only: bool = False):
        if not guild:
            return not guild_only
        query = f"SELECT {plugin} FROM {PLUGINS_TABLE_NAME} WHERE guild_id=?"
        async with self.conn.execute(query, (guild.id,)) as cursor:
            if enabled := await cursor.fetchone():
                enabled = enabled[0]
            return enabled

    async def enable_plugin(self, guild: discord.Guild, plugin: str, enable: bool = True):
        await self.bulk_enable_plugin(guild, {plugin: enable})

    async def bulk_enable_plugin(self, guild: discord.Guild, mapping: dict[str, bool]):
        query = f"SELECT * FROM {PLUGINS_TABLE_NAME} WHERE guild_id=?"
        async with self.conn.execute(query, (guild.id,)) as cursor:
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
                VALUES (?,{','.join('?' for _ in range(len(mapping)))})"""
                await cursor.execute(query, (guild.id, *mapping.values()))
