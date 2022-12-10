"""All core database functions."""
import aiosqlite
import discord
import sqlite3

from src.constants import DEFAULT_PREFIX, DEFAULT_LANGUAGE, DATABASE_PATH
from src.utils import Logger


def db():
    return sqlite3.connect(DATABASE_PATH) 


def async_db():
    return aiosqlite.connect(DATABASE_PATH)


async def create_or_fetch_guild(bot, guild: discord.Guild):
    """Fetch the infos of a guild inside the guild table or insert it."""
    async with async_db() as db:
            async with db.execute(f"SELECT * FROM guilds WHERE guild_id=?", (guild.id,)) as cursor:
                data = await cursor.fetchone()
            if not data:
                # Tries to sync the bot's language with the server's one
                language = guild.preferred_locale if guild.preferred_locale in bot.languages else DEFAULT_LANGUAGE
                data = (guild.id, DEFAULT_PREFIX, language,)
                async with db.execute("INSERT INTO guilds (guild_id, prefix, lang) VALUES (?,?,?)", data):
                    await db.commit()
            return data


async def get_prefix(has_guild):
    """Gets the prefix."""
    try:
        guild = has_guild if isinstance(has_guild, discord.Guild) else getattr(has_guild, "guild", None)
        if guild:
            async with async_db() as db:
                async with db.execute("SELECT prefix FROM guilds WHERE guild_id=?", (guild.id,)) as cursor:
                    prefix = await cursor.fetchone()
            if prefix:
                return prefix[0]
    except Exception as e:
        Logger.error(f"Failed getting prefix on guild '{guild or has_guild}'.", e)
    return DEFAULT_PREFIX

async def change_prefix(bot, guild: discord.Guild, prefix: str):
    await create_or_fetch_guild(bot, guild)
    async with async_db() as db:
        async with db.execute("UPDATE guilds SET prefix=? WHERE guild_id=?", (prefix, guild.id,)):
            await db.commit()


async def get_language(has_guild):
    """Gets the language of a guild."""
    try:
        guild = has_guild if isinstance(has_guild, discord.Guild) else getattr(has_guild, "guild", None)
        if guild:
            async with async_db() as db:
                async with db.execute("SELECT lang FROM guilds WHERE guild_id=?", (guild.id,)) as cursor:
                    prefix = await cursor.fetchone()
            if prefix:
                return prefix[0]
    except Exception as e:
        Logger.error(f"Failed getting language on guild '{guild or has_guild}'.", e)
    return DEFAULT_LANGUAGE

async def change_language(bot, guild: discord.Guild, language: str):
    await create_or_fetch_guild(bot, guild)
    async with async_db() as db:
        async with db.execute("UPDATE guilds SET lang=? WHERE guild_id=?", (language, guild.id,)):
            await db.commit()


async def plugin_is_enabled(has_guild, plugin: str, guild_only: bool = False):
    guild = has_guild if isinstance(has_guild, discord.Guild) else getattr(has_guild, "guild", None)
    if not guild:
        return not guild_only
    async with async_db() as db:
        async with db.execute(f"SELECT enabled FROM {plugin}_plugin WHERE guild_id=?", (guild.id,)) as cursor:
            enabled = await cursor.fetchone()
            if enabled:
                enabled = enabled[0]
            return enabled

async def enable_plugin(guild: discord.Guild, plugin: str, enable: bool = True):
    async with async_db() as db:
        cursor = await db.execute(f"SELECT * FROM {plugin}_plugin WHERE guild_id=?", (guild.id,))
        if not await cursor.fetchone():
            await cursor.execute(f"INSERT INTO {plugin}_plugin (guild_id, enabled) VALUES (?,?)", (guild.id, enable,))
        else:
            await cursor.execute(f"UPDATE {plugin}_plugin SET enabled=? WHERE guild_id=?", (enable, guild.id,))
        await db.commit()
        await cursor.close()