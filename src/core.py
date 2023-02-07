"""Shibbot's base."""
import asyncio
import os
import discord
from discord.ext import bridge
from datetime import datetime, timedelta
from traceback import format_exc
from time import perf_counter

from . import utils, database
from .utils.hardware import Uptime, ServerSpecifications, auto_gc
from .logging import Logger, PStyles
from .console import Console
from .constants import COGS_PATH, SHIBZEL_ID, EXTENSIONS_PATH, OPTIONAL_COGS, CORE_COGS
from .models import PluginCog


MAX_PROCESS_TIMES_LEN = 10000

logger = Logger(__name__)

async def get_that_mf_prefix(amogus, ctx): # "amogus" here is the bot instance
    return await database.get_prefix(ctx)

class Shibbot(bridge.Bot):
    """Subclass of `bridge.Bot`, our little Shibbot :3.
    
    Attributes
    ----------
    debug_mode: `bool`
        Whatever the bot is in debug mode or not.
    extention_path: `str`
        Where the extentions are located.
    init_time: `datetime.datetime`
        The UTC datetime the bot initialized.
    is_alive: `bool`
        Whaterver the bot is alive or not. None if the bot never connected to Discord.
    languages: `list`
        The list of languages that the bot supports.
    reddit: `.utils.reddit.Reddit`
        The reddit client. Can be None.
    repidapi_token: `str`
        The Rapid API token for some commands. Can be None.
    process_times: `list`
        A list of times it took for the commands to execute (in sec).
    invoked_commands: `int`
        The number of commands that have been invoked since initialization."""

    def __init__(self, debug = False, instance_owners: list[int] = None,
                 use_optional_cogs: bool = True, extentions_path: str | None = None, 
                 gc_clear: bool = False, gc_sleep: float = 60.0, gc_max_ram: float = 80.0,
                 *args, **kwargs):
        """Parameters
        ----------
        debug: `bool`
            Whatever the bot is in debug mode or not.
        instance_owners: List[`int`]
            The ids of the owner(s) of this bot instance.
        use_optional_cogs: `bool`
            Whatever you want to load the optional builtin cogs.
        extention_path: `str`
            Where the extentions are located.
        gc_clear: `bool`
            If the automatic garbage collector must be enabled.
        gc_time: `float`
            The time in seconds to wait before the auto gc checks if it must run.
        gc_max_ram: `float`
            The maximum percentage of ram to exceed.
        args: `tuple` & kwargs: dict[`str`, `object`]
            Arguments that are directly passed into `bridge.Bot`.
        """
        logger.log("Initializing Shibbot...")
        start_time = perf_counter()
        
        self.debug_mode = debug
        if self.debug_mode:
            logger.warn("Debug/beta mode is enabled.")
        self.extentions_path = extentions_path or EXTENSIONS_PATH
        
        self.init_time = datetime.utcnow()
        self.is_alive = None
        self.languages = []
        self.process_times = []
        self.invoked_commands = 0

        super().__init__(command_prefix=get_that_mf_prefix,
                         owner_ids=[SHIBZEL_ID] if instance_owners in (None, []) else instance_owners,
                         # Being mentionned by a bot is very annoying, that's why it's all set to False.
                         allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=True, replied_user=False),
                         intents=discord.Intents(
                            bans=True,
                            dm_messages=True, # Waterver we want the bot to respond to dms or not
                            emojis=True,          
                            guild_messages=True,
                            guild_reactions=False, # Not needed yet
                            guilds=True,
                            invites=False,
                            members=True,
                            message_content=True,
                            presences=True,
                            voice_states=False),
                         case_insensitive=True,
                         activity=discord.Streaming(name="connecting...", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ") if use_optional_cogs else None, 
                         *args, **kwargs)                               # Don't put this link on your browser or you might regret it.
        super().remove_command("help")
        
        # Console object
        self.console = Console(self)

        # Client that gets the specifications of the bot
        self.specs = ServerSpecifications(bot=self)

        # Runs gc if the program is going to run out of memory
        if gc_clear:
            logger.warn(f"Automatic garbage collector enabled. Running it every {gc_sleep} sec.")
            self.loop.create_task(auto_gc(self.specs, gc_sleep, gc_max_ram))

        # Synchronous clients for Sqlite3
        self.db = database.db()
        self.cursor = self.db.cursor()
        # Creating default guild table
        self.cursor.execute("CREATE TABLE IF NOT EXISTS guilds(guild_id INTEGER PRIMARY KEY, prefix TEXT, lang TEXT)")
        self.db.commit()

        # Loading all extensions and cogs
        logger.log("Loading cogs...")
        # Builtins cogs
        builtin_path = utils.convert_to_import_path(COGS_PATH) # Converts "./module/submodule" into "module.submodule"
        builtins_cogs = [f"{builtin_path}.{cog}" for cog in CORE_COGS]
        if use_optional_cogs:
            builtins_cogs.extend(f"{builtin_path}.{cog}" for cog in OPTIONAL_COGS)
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
            except ImportError as e:
                logger.error(f"Couldn't import the necessary modules for the extension '{cog}'."
                            " See if there is a requirements.txt inside the folder and then install the dependencies.", e)
            except Exception as e:
                logger.error(f"Couldn't load cog '{cog}'.", e)
        
        if not os.path.exists("./burgir.jpg"):
            logger.log("File 'burgir.jpg' is missing, why did you delete it ???")
            # Really ?! Why ???
            
        logger.log(f"Finished initialization : {len(self.languages)} languages and {len(self.plugins)} plugins for {len(self.cogs)} cogs."
                   f" Took {(perf_counter()-start_time)*1000:.2f} ms.")

    @property
    def plugins(self) -> dict[str, PluginCog]:
        """A read-only mapping of plugin name to PluginCog.

        Returns
        -------
        dict[`str`, `.models.PluginCog`]
        """
        return {cog.plugin_name: cog for cog in self.cogs.values() if isinstance(cog, PluginCog)}
    
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
        if length_processing_times:= len(self.process_times): # Returns True if the length != 0
            return sum(self.process_times)/length_processing_times*1000
        return 0 # The list is empty
        
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
        logger.log("Connecting... wait a few seconds.", PStyles.OKBLUE)
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
        logger.error("Shibbot is being stopped, goodbye !", error)
        await asyncio.gather(self.specs.close(), super().close())
        self.loop.close()
        self.db.close()
        if error: raise error

    def add_bot(self, cls: object) -> object:
        """Adds the bot to the class if it has the attribute `bot`. 

        Returns
        -------
        `object`: The instance of your object with the bot.
        """
        cls.bot = self # Maybe useless ?
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
            raise TypeError(f"'language' must be an 'str' object and not '{type(language).__name__}'")
        if language not in self.languages:
            logger.debug(f"Adding '{language}' language code in the language list.")
            self.languages.append(language)
            
    async def handle_command_error(self, ctx, error):
        for cog in self.cogs.values():
            if type(cog).__name__ == "Events": # Bad way to do this.
                await cog.handle_error(ctx, error)
                break
        
    async def _perf_command(self, method, ctx) -> None:
        if not ctx.command:
            return
        
        start_time = perf_counter()
        await method(ctx)
        result = perf_counter() - start_time
        
        self.process_times.append(result)
        if len(self.process_times) > MAX_PROCESS_TIMES_LEN:
            self.process_times = self.process_times[1:]
        self.invoked_commands += 1
        
        on_guild = f" on guild '{ctx.guild}' (ID: {ctx.guild.id})" if ctx.guild else ""
        logger.debug(f"User '{ctx.author}' (ID: {ctx.author.id}) is running the command '{ctx.command}'{on_guild}. Took {result*1000:.2f}ms.")
    async def invoke(self, ctx):
        await self._perf_command(super().invoke, ctx)
    async def invoke_application_command(self, ctx):
        await self._perf_command(super().invoke_application_command, ctx)
        
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
        if before.content != after.content and before.created_at.timestamp() >= (datetime.utcnow()-timedelta(minutes=5)).timestamp():
            await self.process_commands(after)

    async def on_ready(self) -> None:
        if self.is_alive is None:
            self.invite_bot_url = f"https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=8&scope=bot%20applications.commands"
            logger.log(f"Setting bot invitation link as '{self.invite_bot_url}'.")
            
            self.project_owner = await self.get_or_fetch_user(SHIBZEL_ID)
            self.instance_owners = await asyncio.gather(*[self.get_or_fetch_user(_id) for _id in self.owner_ids])
            logger.log("The following users are the owners of this instance : {0}.".format(", ".join(f"'{user}'" for user in self.instance_owners)))
        elif self.is_alive is False:
            await self.on_resumed()
        self.is_alive = True
        logger.log(f"Ready. Connected as '{self.user}' (ID : {self.user.id}).", PStyles.OKGREEN)

    async def on_resumed(self) -> None:
        self.is_alive = True
        logger.debug("Resuming.")

    async def on_disconnect(self) -> None:
        if self.is_alive is not False:
            self.is_alive = False
            logger.debug("Disconnected.")
            
            await asyncio.sleep(60)
            if self.is_alive is False:
                logger.error("Shibbot has been offline for over a minute, maybe there are network issues ?")

    async def on_guild_join(self, guild: discord.Guild) -> None:
        logger.debug(f"Joined guild '{guild.name}' (ID: {guild.id}).")

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        logger.debug(f"Left guild '{guild.name}' (ID: {guild.id}). Goodbye.")

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        logger.error(f"Ignoring exception in {event_method}: \n{PStyles.ENDC}-> {format_exc()}")

class PterodactylShibbot(Shibbot):
    """A subclass of `Shibbot` using the Pterodactyl API for hardware usage."""

    def __init__(self, ptero_url: str = None, ptero_token: str = None, ptero_server_id: str = None, ptero_refresh: float = 15.0, *args, **kwargs):
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
        self.specs = ServerSpecifications(bot=self, using_ptero=True,
                                                        ptero_url=ptero_url, ptero_token=ptero_token, ptero_server_id=ptero_server_id, secs_looping=ptero_refresh)