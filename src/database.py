import sqlite3
import os
import asyncio
import discord
from discord.ext import commands, bridge

from .constants import DEFAULT_PREFIX, DEFAULT_LANGUAGE


GUILD_TABLE_NAME = "guilds"
PLUGINS_TABLE_NAME = "plugins"
STATS_TABLE_NAME = "stats"

IsOrHasGuild = discord.Guild | commands.Context | bridge.BridgeContext | discord.User

def is_or_has_guild(obj: IsOrHasGuild):
    return obj if isinstance(obj, discord.Guild) else getattr(obj, "guild", None)

class SqliteDatabase(sqlite3.Connection):
    def __init__(self, bot, path: str, *args, **kwargs):
        self.bot = bot
        self.logger = bot.logger.get_logger(__name__)
        self.path = path

        self.logger.debug(f"Connecting to database with synchronous client.")
        if not os.path.exists(self.path):
            open(self.path, "x").close()
            self.logger.warn(f"Missing {self.path} file, creating one.")
        super().__init__(path, *args, **kwargs)

        # Creating default tables and setting up cache
        self.logger.debug(f"Cache allocation for SQLite database in '{self.bot.sqlite_cache_type}': {round(self.bot.sqlite_cache_size/1000, 2)}MB.")
        query = f"""
        PRAGMA cache_size=-{self.bot.sqlite_cache_size};
        PRAGMA temp_store={self.bot.sqlite_cache_type};
        CREATE TABLE IF NOT EXISTS stats (
            bot_id                 INTEGER PRIMARY KEY,
            commands_invoked       INTEGER DEFAULT 0,
            slash_commands_invoked INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS {GUILD_TABLE_NAME} (
            guild_id               INTEGER PRIMARY KEY,
            prefix                 TEXT NOT NULL,
            lang                   TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS {PLUGINS_TABLE_NAME} (
            guild_id               INTEGER PRIMARY KEY
        )"""
        self.executescript(query) # VER: 1.0.0
        self.commit()

    def _init_stats(self, sleep=300):
        bot_id = self.bot.user.id
        query = f"SELECT commands_invoked, slash_commands_invoked FROM {STATS_TABLE_NAME} WHERE bot_id=?"
        cur = self.execute(query, (bot_id,))
        if result := cur.fetchone():
            self.bot.commands_invoked, self.bot.slash_commands_invoked = result
        else:
            query = f"INSERT INTO {STATS_TABLE_NAME} (bot_id) VALUES (?)"
            cur.execute(query, (bot_id,))
            self.commit()
        
        async def loop():
            self._update_stats()
            await asyncio.sleep(sleep)
        self.bot.loop.create_task(loop())

    def _update_stats(self):
        query = f"UPDATE stats SET commands_invoked=?, slash_commands_invoked=? WHERE bot_id=?"
        try:
            self.execute(query, (self.bot.commands_invoked, self.bot.slash_commands_invoked, self.bot.user.id,))
            self.commit()
        except sqlite3.OperationalError as err:
            self.logger.error(
                f"The stats couldn't be updated, probably because the table '{STATS_TABLE_NAME}' doesn't exist yet.",
                err)
        except AttributeError as err:
            self.logger.error("The bot is not ready yet.", err)

    def create_or_fetch_guild(self, bot, guild: discord.Guild):
        """Fetch the infos of a guild inside the guild table or insert it."""
        query = f"SELECT * FROM guilds WHERE guild_id=?"
        cur = self.execute(query, (guild.id,))
        if data := cur.fetchone():
            return data
        # Tries to sync the bot's language with the server's one
        language = (guild.preferred_locale 
            if guild.preferred_locale in bot.languages
            else DEFAULT_LANGUAGE)
        data = (guild.id, DEFAULT_PREFIX, language,)
        self.logger.debug(f"Inserting new guild '{guild.name}' into database. Row: {data}")
        query = "INSERT INTO guilds (guild_id, prefix, lang) VALUES (?, ?, ?)"
        self.execute(query, data)
        self.commit()
        return data

    def get_prefix(self, guild: discord.Guild):
        """Gets the prefix."""
        try:
            if guild:
                query = "SELECT prefix FROM guilds WHERE guild_id=?"
                cur = self.execute(query, (guild.id,))
                if prefix := cur.fetchone():
                    return prefix[0]
        except Exception as e:
            self.logger.debug(f"Couldn't fetch prefix from guild '{guild.name}' (ID: {guild.id}) from database:", e)
        return DEFAULT_PREFIX

    def change_prefix(self, bot, guild: discord.Guild, prefix: str):
        self.create_or_fetch_guild(bot, guild)
        self.logger.debug(f"Updating prefix on guild '{guild.name}' (ID: {guild.id}) for '{prefix}'.")
        query = "UPDATE guilds SET prefix=? WHERE guild_id=?"
        self.execute(query, (prefix, guild.id,))
        self.commit()

    def get_language(self, guild: discord.Guild):
        """Gets the language of a guild."""
        try:
            if guild:
                query = "SELECT lang FROM guilds WHERE guild_id=?"
                cur = self.execute(query, (guild.id,))
                if lang := cur.fetchone():
                    return lang[0]
        except Exception as e:
            self.logger.debug(f"Couldn't fetch language from guild '{guild.name}' (ID: {guild.id}) from database:", e)
        return DEFAULT_LANGUAGE

    def change_language(self, bot, guild: discord.Guild, language: str):
        self.create_or_fetch_guild(bot, guild)
        self.logger.debug(f"Updating language on guild '{guild.name}' (ID: {guild.id}) for '{language}'.")
        query = "UPDATE guilds SET lang=? WHERE guild_id=?"
        self.execute(query, (language, guild.id,))

    def plugin_is_enabled(self, guild: discord.Guild, plugin: str, 
                                guild_only: bool = False):
        if not guild:
            return not guild_only
        query = f"SELECT {plugin} FROM {PLUGINS_TABLE_NAME} WHERE guild_id=?"
        cur = self.execute(query, (guild.id,))
        if enabled := cur.fetchone():
            enabled = enabled[0]
        return enabled

    def add_plugin_table(self, name: str):
        try:
            self.execute(f"SELECT {name} FROM plugins")
        except sqlite3.OperationalError:
            self.logger.debug(f"Adding '{name}' to 'plugin' table in database.")
            self.execute(f"ALTER TABLE plugins ADD COLUMN {name} BOOLEAN DEFAULT 1")
        self.commit() # VER: 1.0.0

    def enable_plugin(self, guild: discord.Guild, plugin: str, enable: bool = True):
        self.bulk_enable_plugin(guild, {plugin: enable})

    def bulk_enable_plugin(self, guild: discord.Guild, mapping: dict[str, bool]):
        self.logger.debug(f"Updating plugins tables for '{guild.name}' (ID: {guild.id}): {mapping}")
        query = f"SELECT * FROM {PLUGINS_TABLE_NAME} WHERE guild_id=?"
        cur = self.execute(query, (guild.id,))
        if cur.fetchone():
            query = f"""
            UPDATE {PLUGINS_TABLE_NAME}
            SET {', '.join(f'{k}=?' for k in mapping.keys())}
            WHERE guild_id=?"""
        else:
            query = f"""
            INSERT INTO {PLUGINS_TABLE_NAME} (
                {', '.join(mapping.keys())},
                guild_id
            )
            VALUES (? ,{', '.join('?' for _ in range(len(mapping)))})"""
        cur.execute(query, (*mapping.values(), guild.id))
        self.commit()
