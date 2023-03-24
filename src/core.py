"""Shibbot's base."""
import os
import random
import asyncio
from datetime import datetime, timedelta
from traceback import format_exc
from time import perf_counter
import discord
from discord.ext import bridge, commands as cmmds

from . import utils, database
from .utils.hardware import Uptime, ServerSpecifications, PteroContainerSpecifications
from .logging import Logger, PStyles
from .models import PluginCog, BaseCog
from .constants import (COGS_PATH, SHIBZEL_ID, EXTENSIONS_PATH,
                        OPTIONAL_COGS, CORE_COGS)
from .console import Console


logger = Logger(__name__)


MAX_PROCESS_TIMES_LEN = 10000


async def get_that_mf_prefix(amogus, ctx):
    return await database.get_prefix(ctx)


class Shibbot(bridge.Bot):
    """Subclass of `bridge.Bot`, our little Shibbot :3."""

    def __init__(self, debug: bool = False, instance_owners: list[int] = None, caching: bool = False,
                 use_optional_cogs: bool = True, extentions_path: str | None = None,
                 *args, **kwargs):
        """Parameters
        ----------
        debug: `bool`
            Whatever the bot is in debug mode or not.
        instance_owners: List[`int`]
            The ids of the owner(s) of this bot instance.
        caching: `bool`
            Whatever the caching is enabled or not.
        use_optional_cogs: `bool`
            Whatever you want to load the optional builtin cogs.
        extention_path: `str`
            Where the extentions are located.
        args: `tuple` & kwargs: dict[`str`, `object`]
            Arguments that are directly passed into `bridge.Bot`.
        """
        logger.log("Initializing Shibbot...")
        start_time = perf_counter()

        self.set_debug(debug)
        if self.debug_mode:
            logger.warn("Debug/beta mode enabled.")
        self.caching = caching
        if self.caching:
            logger.warn("Caching enabled. Note that this option offers higher disponibility"
                        " for some ressources but can increase the RAM and disk usage.")
        self.extentions_path = extentions_path or EXTENSIONS_PATH
        self.instance_owners = None
        self.project_owner = None
        self.init_time = datetime.utcnow()
        self.is_alive = None
        self.languages = []
        self.process_times = []
        self.commands_invoked = 0
        self.slash_commands_invoked = 0
        self.invite_bot_url = None
        self._error_handler = None
        self.cache = {}

        super().__init__(command_prefix=get_that_mf_prefix,
                         owner_ids=[SHIBZEL_ID] 
                            if instance_owners in (None, []) 
                            else instance_owners,
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
                             url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
                                if use_optional_cogs else None,
                         *args, **kwargs)
        super().remove_command("help")

        # Console object
        self.console = Console(self)

        # Client that gets the specifications of the bot
        self.specs = ServerSpecifications()

        # Synchronous clients for Sqlite3
        self.db = database.db()
        self.cursor = self.db.cursor()
        # Creating default guild table
        query = "CREATE TABLE IF NOT EXISTS " + \
                "guilds(guild_id INTEGER PRIMARY KEY, prefix TEXT, lang TEXT)"
        self.cursor.execute(query)
        self.db.commit()

        # Loading all extensions and cogs
        logger.log("Loading cogs...")
        # Builtins cogs
        # Converts "./module/submodule" into "module.submodule"
        builtin_path = utils.convert_to_import_path(COGS_PATH)
        builtins_cogs = [f"{builtin_path}.{cog}" for cog in CORE_COGS]
        if use_optional_cogs:
            builtins_cogs.extend(
                f"{builtin_path}.{cog}" for cog in OPTIONAL_COGS)
        for cog in builtins_cogs:
            self.load_extension(cog)
        # Extensions
        extension_path = utils.convert_to_import_path(self.extentions_path)
        extensions = []
        for extension in os.listdir(self.extentions_path):
            if extension in ("__pycache__",) or extension.endswith((".md",)):
                continue
            if extension.endswith(".py"):
                extension = extension[:-3]
            extensions.append(f"{extension_path}.{extension}")
        for cog in extensions:
            try:
                self.load_extension(cog)
                continue
            except ImportError as exc:
                logger.error(f"Couldn't import the necessary modules for the extension '{cog}'."
                             " See if there is a requirements.txt inside the folder "
                             "and then install the dependencies.", exc)
            except Exception as err:
                logger.error(f"Couldn't load cog '{cog}'.", err)

        if not os.path.exists("./burgir.jpg"):
            logger.warn("File 'burgir.jpg' is missing, why did you delete it ???")
            # Really ?! Why ???

        logger.log(f"Finished initialization : {len(self.languages)} languages"
                   f", {len(self.get_commands())} commands for {len(self.cogs)} cogs ({len(self.plugins)} plugins)."
                   f" Took {(perf_counter()-start_time)*1000:.2f} ms.", PStyles.OKCYAN)

    @property
    def plugins(self) -> dict[str, PluginCog]:
        """A read-only mapping of plugin name to PluginCog.

        Returns
        -------
        dict[`str`, `.models.PluginCog`]
        """
        return {cog.plugin_name: cog
                for cog in self.cogs.values()
                if isinstance(cog, PluginCog)}
        
    @property
    def cogs(self) -> dict[str, discord.Cog]:
        """A read-only sorted mapping of cog name to cog."""
        return dict(sorted(super().cogs.items()))

    @property
    def uptime(self) -> Uptime:
        """The uptime of the bot.

        Returns
        -------
        `Uptime`:  An instance of `.utils.Uptime`.
        """
        return Uptime(self.init_time)

    @property
    def avg_processing_time(self) -> float:
        """The average processing time of the bot for a command.
        
        Returns
        -------
        `float`: The average in ms.
        """
        if length_processing_times := len(self.process_times):  # Returns True if the length != 0
            return sum(self.process_times)/length_processing_times*1000
        return 0  # The list is empty
    
    @property
    def invoked_commands(self) -> int:
        return self.commands_invoked + self.slash_commands_invoked
    
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

    def add_bot(self, cls: object) -> object:
        """Adds the bot to the class if it has the attribute `bot`. 

        Returns
        -------
        `object`: The instance of your object with the bot.
        """
        cls.bot = self  # Maybe useless ?
        return cls

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
            raise TypeError(
                f"'language' must be an 'str' object and not '{type(language).__name__}'")
        if language not in self.languages:
            logger.debug(f"Adding '{language}' language code in the language list.")
            self.languages.append(language)
            self.languages.sort()
            
    def set_error_handler(self, handler: BaseCog):
        handler.handle_error # Can raise AttributeError
        logger.debug(f"Setting '{repr(handler)}' as new error handler for command exceptions.")
        self._error_handler = handler
            

    async def handle_command_error(self, ctx, error: Exception) -> None:
        if self._error_handler:
            self._error_handler.handle_error(ctx, error)

    def set_debug(self, debug: bool) -> None:
        self.debug_mode = debug
        logger.set_debug(debug)

    async def _perf_command(self, method, ctx: discord.SlashCommand | cmmds.Context) -> None:
        if not ctx.command:
            # I don't remember what this does but i'm pretty sure it's important
            return

        start_time = perf_counter()
        await method(ctx)
        result = perf_counter() - start_time

        self.process_times.append(result)
        if len(self.process_times) > MAX_PROCESS_TIMES_LEN:
            del self.process_times[1:]

        on_guild = (f" on guild '{ctx.guild}' (ID: {ctx.guild.id})" 
                        if ctx.guild else "")
        logger.debug(f"User '{ctx.author}' (ID: {ctx.author.id})"
                     f" is running the command '{ctx.command}'{on_guild}."
                     f" Took {result*1000:.2f}ms.")

    async def invoke(self, ctx: cmmds.Context):
        await self._perf_command(super().invoke, ctx)
        self.commands_invoked += 1

    async def invoke_application_command(self, ctx: discord.ApplicationContext):
        await self._perf_command(super().invoke_application_command, ctx)
        self.slash_commands_invoked += 1

    def _on_cog(self, method, *args, **kwargs) -> None:
        """Fixes a bug beacause using methods like loading must run twice."""
        try:
            method(*args, **kwargs)
        except AttributeError:
            method(*args, **kwargs)

    def load_extension(self, name: str, *args, **kwargs):
        logger.debug(f"Initializing cog '{name}'.")
        self._on_cog(super().load_extension, name, *args, **kwargs)

    def unload_extension(self, name: str, *args, **kwargs):
        logger.debug(f"Unloading cog '{name}'.")
        self._on_cog(super().unload_extension, name, *args, **kwargs)

    def reload_extension(self, name: str, *args, **kwargs):
        logger.debug(f"Reloading cog '{name}'.")
        self._on_cog(super().reload_extension, name, *args, **kwargs)

    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.content != after.content:
            five_minutes_ago = (datetime.utcnow()-timedelta(minutes=5)).timestamp()
            if before.created_at.timestamp() >= five_minutes_ago:
                await self.process_commands(after)

    async def on_ready(self) -> None:
        if self.is_alive is None:
            self.invite_bot_url = f"https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=8&scope=bot%20applications.commands"
            underlined_link = PStyles.UNDERLINE + self.invite_bot_url + PStyles.ENDC
            logger.log(f"Setting bot invitation link as {underlined_link}")

            self.project_owner = await self.get_or_fetch_user(SHIBZEL_ID)
            self.instance_owners = await asyncio.gather(
                *[self.get_or_fetch_user(_id) for _id in self.owner_ids])
            users = ", ".join(f"'{user}'" for user in self.instance_owners)
            logger.log(f"The following users are the owners of this instance : {users}.")
        elif self.is_alive is False:
            await self.on_resumed()
        self.is_alive = True
        logger.log(f"☁ Ready. Connected as '{self.user}' (ID : {self.user.id}).",
                   PStyles.OKGREEN)

    async def on_resumed(self) -> None:
        self.is_alive = True
        logger.debug("Resuming.")

    async def on_disconnect(self) -> None:
        if self.is_alive is not False:
            self.is_alive = False
            logger.debug("Disconnected.")

            await asyncio.sleep(60)
            if self.is_alive is False:
                logger.error("Shibbot has been offline for over a minute,"
                             " maybe there are network issues ?")

    async def on_guild_join(self, guild: discord.Guild) -> None:
        logger.debug(f"Joined guild '{guild.name}' (ID: {guild.id}).")

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        logger.debug(f"Left guild '{guild.name}' (ID: {guild.id}). Goodbye.")

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        logger.error(f"Ignoring exception in {event_method}: \n"
                     f"{PStyles.ENDC}-> {format_exc()}")

    def run(self, token: str, command_input: bool = False, *args, **kwargs) -> None:
        """Loads extensions and cogs optionally and runs the bot.

        Parameters
        ----------
        command_input: `bool`
            Accept command input from the user. Defaults to False.
        """
        if command_input:
            self.console.start()
        self.specs.start()
        connect_message = ("🚀 Connecting... wait a few seconds." 
                        if random.randint(0, 99) else "Lodin cheeseburgers...")
        logger.log(connect_message, PStyles.OKBLUE)
        super().run(token, *args, **kwargs)

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
        logger.error("👋 Shibbot is being stopped, goodbye !", error)
        await self.specs.close()
        await super().close()
        self.loop.close()
        self.db.close()
        if error:
            raise error


class PterodactylShibbot(Shibbot):
    """A subclass of `Shibbot` using the Pterodactyl API for hardware usage."""

    def __init__(self, ptero_url: str = None, ptero_token: str = None, ptero_server_id: str = None,
                 ptero_refresh: float = 15.0, *args, **kwargs):
        """Parameters
        ----------
        ptero_url: `str`
            The url to your Pterodactyl Panel.
        ptero_token: `str`
            The token of your panel.
        ptero_server_id: `str`
            The id of the server the bot is running on.
        ptero_refresh: `float`
            The time to wait before getting the usage again.
        args: `tuple` & kwargs: dict[`str`, `object`]
            Arguments that are directly passed into `.Shibbot`."""
        super().__init__(*args, **kwargs)
        logger.debug("Using the Pterodactyl API to get hardware usage.")
        self.specs = PteroContainerSpecifications(
            ptero_url=ptero_url,
            ptero_token=ptero_token,
            ptero_server_id=ptero_server_id,
            secs_looping=ptero_refresh
        )
