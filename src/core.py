import os
import random
import sqlite3
import asyncio
from datetime import datetime, timedelta
from traceback import format_exc
from time import perf_counter
from inspect import iscoroutinefunction
from functools import partial
import discord
from discord.ext import bridge, commands as cmmds

from .database import AsyncDB, GUILD_TABLE_NAME, PLUGINS_TABLE_NAME
from .utils import convert_to_import_path
from .utils import json as jayson
from .utils.hardware import Uptime, ServerSpecifications, PteroContainerSpecifications
from .logging import Logger, ANSIEscape, LoggingLevel
from .models import PluginCog, BaseCog
from .console import Console
from .constants import (
    COGS_PATH, SHIBZEL_ID, EXTENSIONS_PATH,
    OPTIONAL_COGS, CORE_COGS, CACHE_PATH,
    DATABASE_FILE_PATH, TEMPORARY_CACHE_PATH
)


__all__ = ("MAX_PROCESS_TIMES_LEN", "Shibbot", "PterodactylShibbot")


MAX_PROCESS_TIMES_LEN = 10000

async def _get_prefix(bot: "Shibbot", ctx):
    return await bot.asyncdb.get_prefix(ctx)

class Shibbot(bridge.Bot):
    """Subclass of `bridge.Bot`, our little Shibbot :3."""

    def __init__(
            self,
            logger: Logger,
            instance_owners: list[int] = None,
            debug: bool = False,
            caching: bool = False,
            use_optional_cogs: bool = True,
            disabled_cogs: list[str] | None = None,
            database_fp: str | None = DATABASE_FILE_PATH,
            extentions_path: str | None = EXTENSIONS_PATH,
            cache_path: str | None = CACHE_PATH,
            temp_cache_path: str | None = TEMPORARY_CACHE_PATH,
            *args, **kwargs
        ):
        start_time = perf_counter()
        self.logger = logger.get_logger(__name__)
        self.__logger = logger
        self.logger.log("Initializing Shibbot...")
        self.init_time = datetime.utcnow()
        self.debug_mode = debug
        if self.debug_mode:
            self.logger.warn("Debug/beta mode enabled.")
        self._caching = caching
        if self.caching:
            self.logger.warn("Caching enabled. Note that this option offers higher disponibility"
                        " for some ressources but can increase the RAM and disk usage.")
        self.database_fp = database_fp
        self.cache_path = cache_path
        self.temp_cache_path = temp_cache_path
        self.extentions_path = extentions_path
        self.instance_owners = None
        self.project_owner = None
        self.is_alive = None
        self.invite_bot_url = None
        self._error_handler = None
        self._looping_tasks = []
        self.process_times = []
        self.languages = []
        self.cache = {}

        super().__init__(
            command_prefix=_get_prefix,
            owner_ids=[SHIBZEL_ID] if instance_owners in (None, []) else instance_owners,
            # Being mentionned by a bot is very annoying, that's why it's all set to False.
            allowed_mentions=discord.AllowedMentions(
                everyone=False,
                users=True,
                roles=True,
                replied_user=False),
            intents=discord.Intents(
                bans=True,
                dm_messages=True,  # Waterver we want the bot to respond to dms or not
                emojis=True,
                guild_messages=True,
                guild_reactions=False,  # Not needed yet
                guilds=True,
                invites=False,
                members=True,
                message_content=True,
                presences=True,
                voice_states=False),
            case_insensitive=True,
            activity=discord.Streaming(
                name="connecting...",
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ") if use_optional_cogs else None,
            *args, **kwargs
        )
        super().remove_command("help")

        # Statistics
        stats_fp = self.cache_path + "/stats.json"
        self._stats = jayson.load(stats_fp) if os.path.exists(stats_fp) else {}
        async def callback(): jayson.dump(self._stats, stats_fp)
        self.loop_task(callback, time=300)
        
        # Console object
        self.console = Console(self)

        # Client that gets the specifications of the bot
        self.specs = ServerSpecifications(self)

        # SQLite3 database
        if not os.path.exists(database_fp):
            open(database_fp, "x")
            self.logger.warn(f"Missing {database_fp} file, creating one.")
        self.db = sqlite3.connect(database_fp)
        self.cursor = self.db.cursor()
        self.asyncdb = AsyncDB(database_fp)
        # Setting up cache
        size, store = ("-10000", "MEMORY") if self.caching else ("-2000", "FILE")
        query = f"PRAGMA cache_size={size}; PRAGMA temp_store={store}"
        self.cursor.executescript(query) # VER: 1.0.0
        # Creating default tables
        query = f"""
        CREATE TABLE IF NOT EXISTS {GUILD_TABLE_NAME} (
            guild_id INTEGER PRIMARY KEY,
            prefix   TEXT NOT NULL,
            lang     TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS {PLUGINS_TABLE_NAME} (
            guild_id INTEGER PRIMARY KEY
        )"""
        self.cursor.executescript(query) # VER: 1.0.0
        self.db.commit()

        # Loading all extensions and cogs
        self.logger.log("Loading cogs...")
        # Builtins cogs
        builtin_path = convert_to_import_path(COGS_PATH)  # Converts "./module/submodule" into "module.submodule"
        builtins_cogs = {f"{builtin_path}.{cog}" for cog in CORE_COGS}
        if use_optional_cogs:
            builtins_cogs |= {f"{builtin_path}.{cog}" for cog in OPTIONAL_COGS}
        disabled_cogs = set(disabled_cogs) if disabled_cogs else set()
        for cog in builtins_cogs - disabled_cogs:
            self.load_extension(cog)
            
        # Extensions
        extension_path = convert_to_import_path(self.extentions_path)
        extensions = []
        exclude = {"__pycache__",}
        for extension in set(os.listdir(self.extentions_path)) - exclude:
            if extension.endswith(".py"):
                extension = extension[:-3]
            extensions.append(f"{extension_path}.{extension}")
        for cog in extensions:
            try:
                self.load_extension(cog)
            except ImportError as exc:
                self.logger.error(f"Couldn't import the necessary modules for the extension '{cog}'."
                             " See if there is a requirements.txt inside the folder "
                             "and then install the dependencies.", exc)
            except Exception as err:
                self.logger.error(f"Couldn't load cog '{cog}'.", err)

        if not os.path.exists("./burgir.jpg"):
            self.logger.warn("File 'burgir.jpg' is missing, why did you delete it ???")
            # Really ?! Why ???

        self.logger.log(
            f"Finished initialization : {len(self.languages)} languages"
            f", {len(self.get_commands())} commands for {len(self.cogs)} cogs ({len(self.plugins)} plugins)."
            f" Took {(perf_counter()-start_time)*1000:.2f} ms.", ANSIEscape.cyan)
        
    async def __async_init__(self) -> None:
        await self.asyncdb
        
    async def start(self, *args, **kwargs) -> None:
        await self.__async_init__()
        return await super().start(*args, **kwargs)
        
    def loop_task(self, callback, *args, time: int, **kwargs) -> None:
        async def loop():
            while self.loop.is_running():
                await callback(*args, **kwargs)
                await asyncio.sleep(time)
        self._looping_tasks.append(callback(*args, **kwargs))
        self.loop.create_task(loop())
                
    @property
    def caching(self) -> bool:
        return self._caching
    
    @property
    def debug_mode(self) -> bool:
        return self._debug_mode

    @debug_mode.setter
    def debug_mode(self, value: bool) -> None:
        self.__logger.level = LoggingLevel.debug if value else LoggingLevel.info
        self._debug_mode = value

    @property
    def uptime(self) -> Uptime:
        return Uptime(self.init_time)

    async def on_ready(self) -> None:
        if self.is_alive is None:
            self.invite_bot_url = f"https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=8&scope=bot%20applications.commands"
            underlined_link = ANSIEscape.underline + self.invite_bot_url + ANSIEscape.endc
            self.logger.log(f"Setting bot invitation link as {underlined_link}")

            self.project_owner = await self.get_or_fetch_user(SHIBZEL_ID)
            self.instance_owners = await asyncio.gather(
                *[self.get_or_fetch_user(_id) for _id in self.owner_ids])
            users = ", ".join(f"'{user}'" for user in self.instance_owners)
            self.logger.log(f"The following users are the owners of this instance : {users}.")
        elif self.is_alive is False:
            await self.on_resumed()
        self.is_alive = True
        self.logger.log(f"☁ Ready. Connected as '{self.user}' (ID : {self.user.id}).",
                   ANSIEscape.green)

    async def on_resumed(self) -> None:
        self.is_alive = True
        self.logger.debug("Resuming.")

    async def on_disconnect(self) -> None:
        if self.is_alive is not False:
            self.is_alive = False
            self.logger.debug("Disconnected.")

            await asyncio.sleep(60)
            if self.is_alive is False:
                self.logger.error("Shibbot has been offline for over a minute,"
                             " maybe there are network issues ?")

    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.content != after.content:
            five_minutes_ago = (datetime.utcnow()-timedelta(minutes=5)).timestamp()
            if before.created_at.timestamp() >= five_minutes_ago:
                await self.process_commands(after)

    async def on_guild_join(self, guild: discord.Guild) -> None:
        self.logger.debug(f"Joined guild '{guild.name}' (ID: {guild.id}).")

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        self.logger.debug(f"Left guild '{guild.name}' (ID: {guild.id}). Goodbye.")

    def add_language(self, language: str) -> None:
        """Adds a language to the bot.

        Parameters
        ----------
        language: `str`
            Must be an language code like `en`, `de` or `fr`.

        Raises
        ------
        `TypeError`: `language` isn't an str object.
        """
        if not isinstance(language, str):
            raise TypeError("language must be an str.")
        if language not in self.languages:
            self.logger.debug(f"Adding '{language}' language code in the language list.")
            self.languages.append(language)
    
    @property
    def commands_invoked(self) -> int:
        key = "commands_invoked"
        if not self._stats.get(key):
            self._stats[key] = 0
        return self._stats[key]
    
    @commands_invoked.setter
    def commands_invoked(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("value must be an int.")
        self._stats["commands_invoked"] = value
        
    @property
    def slash_commands_invoked(self) -> int:
        key = "slash_commands_invoked"
        if not self._stats.get(key):
            self._stats[key] = 0
        return self._stats[key]
    
    @slash_commands_invoked.setter
    def slash_commands_invoked(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("value must be an int.")
        self._stats["slash_commands_invoked"] = value
    
    @property
    def invoked_commands(self) -> int:
        return self.commands_invoked + self.slash_commands_invoked

    @property
    def avg_processing_time(self) -> float:
        """The average processing time of the bot for a command.
        
        Returns
        -------
        `float`: The average in ms.
        """
        if length_processing_times := len(self.process_times):  # Returns True if the length != 0
            return sum(self.process_times)/length_processing_times*1000
        return 0.  # The list is empty

    async def _invoke(self, method, ctx: discord.SlashCommand | cmmds.Context) -> None:
        coro = method(ctx)
        if not ctx.command:
            return await coro
        
        start_time = perf_counter()
        result = await coro
        time_took = perf_counter() - start_time

        self.process_times.append(time_took)
        if len(self.process_times) > MAX_PROCESS_TIMES_LEN:
            del self.process_times[1:]

        on_guild = (f" on guild '{ctx.guild}' (ID: {ctx.guild.id})" 
                        if ctx.guild else "")
        self.logger.debug(f"User '{ctx.author}' (ID: {ctx.author.id})"
                    f" is running the command '{ctx.command}'{on_guild}."
                    f" Took {time_took*1000:.2f}ms.")
        return result

    async def invoke(self, ctx: cmmds.Context) -> None:
        if ctx.command:
            self.commands_invoked += 1
        return await self._invoke(super().invoke, ctx)

    async def invoke_application_command(self, ctx: discord.ApplicationContext) -> None:
        self.slash_commands_invoked += 1
        return await self._invoke(super().invoke_application_command, ctx)
    
    def get_commands(self, hidden: bool = False) -> set:
        if not hidden:
            return super().commands
        cogs = self.cogs.values()
        _commands = []
        for cog in cogs:
            if getattr(cog, "hidden", True):
                continue
            _commands.extend(cog.get_commands())
        return set(_commands)
        
    @property
    def cogs(self) -> dict[str, discord.Cog]:
        """A read-only sorted mapping of cog name to cog."""
        return dict(sorted(super().cogs.items()))

    @property
    def plugins(self) -> dict[str, PluginCog]:
        return {cog.plugin_name: cog
                for cog in self.cogs.values()
                if isinstance(cog, PluginCog)}

    def _on_cog(self, method, *args, **kwargs) -> None:
        """Fixes a bug beacause using methods like loading must run twice."""
        try:
            res = method(*args, **kwargs)
        except AttributeError:
            res = method(*args, **kwargs)
        return res

    def load_extension(self, name: str, *args, **kwargs):
        self.logger.debug(f"Initializing cog '{name}'.")
        return self._on_cog(super().load_extension, name, *args, **kwargs)

    def unload_extension(self, name: str, *args, **kwargs):
        self.logger.debug(f"Unloading cog '{name}'.")
        return self._on_cog(super().unload_extension, name, *args, **kwargs)

    def reload_extension(self, name: str, *args, **kwargs):
        self.logger.debug(f"Reloading cog '{name}'.")
        return self._on_cog(super().reload_extension, name, *args, **kwargs)
            
    def set_error_handler(self, handler: BaseCog) -> None:
        if not hasattr(handler, "handle_error"):
            raise AttributeError("The error handler must have a async method named 'handle_error()'.")
        self.logger.debug(f"Setting '{repr(handler)}' as new error handler for command exceptions.")
        self._error_handler = handler

    async def handle_command_error(self, ctx, error: Exception) -> None:
        if self._error_handler:
            return await self._error_handler.handle_error(ctx, error)

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        self.logger.error(f"Ignoring exception in {event_method}:", format_exc())

    def run(self, token: str, command_input: bool = False, *args, **kwargs) -> None:
        if command_input:
            self.console.start()
        self.specs.start()
        connect_message = ("🚀 Connecting... wait a few seconds." 
                           if random.randint(0, 99) else "🍔 Lodin cheeseburgers...")
        self.logger.log(connect_message, ANSIEscape.blue)
        return super().run(token, *args, **kwargs)

    async def close(self, error: Exception = None) -> None:
        """Closes the bot.

        Parameters
        ----------
        error: `Exception`
            The error which caused the bot to stop.

        Raises
        ------
        `Exception`: Reraised error, if there is one.
        """
        self.logger.error("👋 Shibbot is being stopped, goodbye !", error)
        await asyncio.gather(
            *self._looping_tasks,
            self.specs.close(),
            self.asyncdb.close(),
        )
        self.db.close()
        await super().close()
        self.loop.stop()
        self.loop.close()
        if error:
            raise error

class PterodactylShibbot(Shibbot):
    """A subclass of `Shibbot` using the Pterodactyl API for hardware usage."""

    def __init__(
            self,
            ptero_url: str = None,
            ptero_token: str = None,
            ptero_server_id: str = None,
            ptero_refresh: float = 15.0,
            *args, **kwargs
        ):
        super().__init__(*args, **kwargs)
        self.logger.debug("Using the Pterodactyl API to get hardware usage.")
        self.specs = PteroContainerSpecifications(
            self,
            ptero_url=ptero_url,
            ptero_token=ptero_token,
            ptero_server_id=ptero_server_id,
            secs_looping=ptero_refresh
        )
