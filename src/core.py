import os
import random
import asyncio
from datetime import datetime, timedelta
from traceback import format_exc
from time import perf_counter
import discord
from discord.ext import bridge, commands

from . import __version__
from .database import SqliteDatabase
from .utils import convert_to_import_path
from .utils import json as ljson
from .utils.hardware import Uptime, ServerSpecifications, PteroContainerSpecifications
from .logging import Logger, ANSIEscape, LoggingLevel
from .models import PluginCog, BaseCog
from .console import Console
from .constants import (
    COGS_PATH, BUILTIN_COGS,
    DATABASE_FILE_PATH, EXTENSIONS_PATH, CACHE_PATH, TEMPORARY_CACHE_PATH,
    SHIBZEL_ID,
)


# SQLite3 default parameters
SQLITE_DEFAULT_CACHE_SIZE = 2000
SQLITE_DEFAULT_CACHE_TYPE = "FILE"

MAX_PROCESS_TIMES_LEN = 10000  # The maximum length of the list of commands process times
PREVIOUS_VERSIONS_FILE_NAME = "/previous_versions.json"
DEFAULT_ALLOWED_MENTIONS = discord.AllowedMentions(
    everyone=False,
    users=True,
    roles=True,
    replied_user=False
)
DEFAULT_INTENTS = discord.Intents(
    bans=True,
    dm_messages=True,  # Whatever we want the bot to respond to dms or not
    emojis=True,
    guild_messages=True,
    guild_reactions=False,  # Not needed yet
    guilds=True,
    invites=False,
    members=True,
    message_content=True,
    presences=True,
    voice_states=False
)

async def _get_prefix(bot: "Shibbot", ctx):
    return bot.db.get_prefix(ctx.guild)

class Shibbot(bridge.Bot):
    """Subclass of `bridge.Bot`, our little Shibbot :3."""

    def __init__(
        self,
        logger: Logger,
        # Base class settings
        instance_owners: list[int] = None,
        mentions: discord.AllowedMentions = DEFAULT_ALLOWED_MENTIONS,
        intents: discord.Intents = DEFAULT_INTENTS,
        default_help_commands: bool = False,  # True: uses the default pycord help command 
                                              # (can conflict if "src.cogs.commands" isn't disabled)

        # Shibbot settings
        debug: bool = False,
        caching: bool = False,
        minimal: bool = False,
        allowed_cogs: list[str] = None,
        disabled_cogs: list[str] = None,
        # Advanced
        database_fp: str = DATABASE_FILE_PATH,
        extensions_path: str = EXTENSIONS_PATH,
        cache_path: str = CACHE_PATH,
        temp_cache_path: str = TEMPORARY_CACHE_PATH,
        sqlite_cache_size: str = SQLITE_DEFAULT_CACHE_SIZE,
        sqlite_cache_type: str = SQLITE_DEFAULT_CACHE_TYPE,
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
            self.logger.warn("Caching enabled. Note that this option offers higher availability"
                " for some resources but can increase the RAM and disk usage.")
        self.database_fp = database_fp
        self.cache_path = cache_path
        self.temp_cache_path = temp_cache_path
        self.extensions_path = extensions_path
        self.sqlite_cache_size = sqlite_cache_size
        self.sqlite_cache_type = sqlite_cache_type
        self.instance_owners: list[discord.User] = None
        self.project_owner: discord.User = None
        self.is_alive = None
        self.last_disconnection: datetime = None
        self.invite_bot_url: str = None
        self._error_handler = None
        self.process_times: list[float] = []
        self.languages: list[str] = []
        self.commands_invoked = 0
        self.slash_commands_invoked = 0

        self.logger.debug("Initializing base class.")
        super().__init__(
            command_prefix=_get_prefix,
            owner_ids=[SHIBZEL_ID] if instance_owners in (None, []) else instance_owners,
            allowed_mentions=mentions,
            intents=intents,
            case_insensitive=True,
            activity=discord.Streaming(
                name="connecting...",
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ") if not minimal else None,
            *args, **kwargs
        )
        if not default_help_commands:
            super().remove_command("help")

        # Cache
        # Previous versions
        prev_v_fp = self.cache_path + PREVIOUS_VERSIONS_FILE_NAME
        self._versions = ljson.load(prev_v_fp) if os.path.exists(prev_v_fp) else []
        if __version__ not in self._versions:
            self._versions.append(__version__)
            ljson.dump(self._versions, prev_v_fp)
        
        # Console object
        self.console = Console(self)

        # Client that gets the specifications of the bot
        self.specs = ServerSpecifications(self)

        # SQLite3 database
        self.db = SqliteDatabase(self, database_fp)

        # Loading extensions and cogs
        disabled_cogs = set(disabled_cogs) if disabled_cogs else set()
        if minimal:
            self.logger.warn("Shibbot started in minimal mode so no default cog will load except allowed ones.")
            cogs = allowed_cogs
        else:
            cogs = BUILTIN_COGS
            
        self.logger.log("Loading cogs...")
        builtin_path = convert_to_import_path(COGS_PATH)  # Converts "./module/submodule" into "module.submodule"
        builtins_cogs = {f"{builtin_path}.{cog}" for cog in cogs}
        for cog in builtins_cogs - disabled_cogs:
            self.load_extension(cog)
            
        # Extensions
        extension_path = convert_to_import_path(self.extensions_path)
        extensions = []
        exclude = {"__pycache__",}
        for extension in set(os.listdir(self.extensions_path)) - exclude:
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
                extensions.remove(cog)
            except Exception as err:
                self.logger.error(f"Couldn't load cog '{cog}'.", err)
        if extensions:
            self.logger.log(f"Loaded {len(extensions)} extensions : {', '.join(extensions)}.")

        if not os.path.exists("./misc/burgir.jpg"):
            self.logger.warn("File 'burgir.jpg' is missing, why did you delete it ???")
            # Really ?! Why ???

        self.logger.log(
            f"Finished initialization : {len(self.languages)} languages"
            f", {len(self.get_commands())} commands for {len(self.cogs)} cogs ({len(self.plugins)} plugins)."
            f" Took {(perf_counter()-start_time)*1000:.2f} ms.", ANSIEscape.cyan)
                
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
    
    @property
    def member_count(self):
        return sum(len(guild.members) for guild in self.guilds)
    
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

    async def on_ready(self) -> None:
        if self.is_alive is None:
            self.db._init_stats()

            self.invite_bot_url = f"https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=8&scope=bot%20applications.commands"
            underlined_link = ANSIEscape.underline + self.invite_bot_url + ANSIEscape.endc
            self.logger.log(f"Setting bot invitation link as {underlined_link}")

            self.logger.debug("Fetching owners and Shibzel's account.")
            self.project_owner = await self.get_or_fetch_user(SHIBZEL_ID)
            self.instance_owners = await asyncio.gather(
                *[self.get_or_fetch_user(_id) for _id in self.owner_ids])
            users = ", ".join(f"'{user}'" for user in self.instance_owners)
            self.logger.log(f"The following users are the owners of this instance : {users}.")
            self.logger.debug(f"Ping: {self.latency*1000:.2f}, servers: {len(self.guilds)}, users: {len(self.users)}.")
        elif self.is_alive is False:
            await self.on_resumed()
        self.is_alive = True
        self.logger.log(f"☁ Ready. Connected as '{self.user}' (ID : {self.user.id}).",
                        ANSIEscape.green)

    async def on_resumed(self) -> None:
        self.is_alive = True
        dtime = datetime.utcnow().timestamp() - self.last_disconnection.timestamp()
        log = "Resuming" + (f" (has been disconnected for {dtime} sec)." if dtime > 10 else ".")
        self.logger.debug(log)

    async def on_disconnect(self) -> None:
        self.last_disconnection = datetime.utcnow()
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
        #return await super().on_message_edit()  # Only an event ?

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

    async def _invoke(self, method, ctx: discord.SlashCommand | commands.Context) -> None:
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

    async def invoke(self, ctx: commands.Context) -> None:
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
        self.logger.debug(f"Setting '{type(handler).__module__}' as error handler for command exceptions.")
        self._error_handler = handler

    async def handle_command_error(self, ctx, error: Exception) -> None:
        if self._error_handler:
            return await self._error_handler.handle_error(ctx, error)

    async def on_error(self, event_method: str, *args) -> None:
        self.logger.error(f"Ignoring exception in {event_method}:", format_exc())

    def run(self, token: str, command_input: bool = False, *args, **kwargs) -> None:
        if command_input:
            self.loop.call_soon(asyncio.ensure_future, self.console.run())
        self.specs.start()
        connect_message = ("🚀 Connecting... wait a few seconds."  # 99% chance of happening
                           if random.randint(0, 99) else "🍔 Lodin cheeseburgers...")  # 1%
        self.logger.log(connect_message, ANSIEscape.blue)
        return super().run(token, *args, **kwargs)

    async def close(self, error: Exception = None) -> None:
        self.logger.error("👋 Shibbot is being stopped, goodbye !", error)
        self.db._update_stats()
        self.db.close()
        await asyncio.gather(
            self.specs.close(),
            # ...
        )
        self.console.stop()
        for cog in tuple(self.extensions):
            try:
                self.unload_extension(cog)
            except Exception as err:
                self.logger.error(f"Couldn't unload cog '{cog}'.", err)
        await super().close()
        self.loop.stop()
        self.loop.close()
        self.logger.debug("Loop closed.")

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
