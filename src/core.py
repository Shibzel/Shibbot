"""Shibbot's base."""
import discord
from discord.ext import bridge
from asyncio import gather
from datetime import datetime, timedelta
from traceback import format_exc
from os import listdir, path
from time import perf_counter

from . import database, utils
from .utils import hardware, reddit
from .logging import Logger, PStyles
from .console import Console
from .constants import COGS_PATH, SHIBZEL_ID, EXTENSIONS_PATH, BUILTIN_COGS
from .models import PluginCog


MAX_PROCESS_TIMES_LEN = 1000

logger = Logger(__name__)

def bot_get_prefix(bot, ctx):
    return database.get_prefix(ctx)

class Shibbot(bridge.Bot):
    """Subclass of `bridge.Bot`, our little Shibbot :3."""

    def __init__(self, test_mode = False, instance_owners: list[int] = None, extentions_path: str | None = None,
                 gc_clear: bool = False, gc_sleep: float = 60.0, gc_max_ram: float = 80.0,
                 *args, **kwargs):
        self.test_mode = test_mode
        self.extentions_path = extentions_path or EXTENSIONS_PATH
        
        logger.log("Initializing Shibbot...")
        start_time = perf_counter()
        self.init_time = datetime.utcnow()
        
        if self.test_mode:
            logger.warn("Test/beta mode is enabled.")
        self.is_alive = None
        self.languages = []
        self.reddit: reddit.Reddit = None
        self.process_times = []
        self.invoked_commands = 0

        super().__init__(command_prefix=bot_get_prefix,
                        owner_ids=[SHIBZEL_ID] if instance_owners in (None, []) else instance_owners,
                        # Being mentionned by a bot is very annoying, that's why it's all set to False.
                        allowed_mentions=discord.AllowedMentions.none(),
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
                        activity=discord.Streaming(
                            name="connecting...",
                            # Don't put this link on your browser or you'll regret it.
                            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
                        *args, **kwargs)
        super().remove_command("help")

        # Client that gets the specifications of the bot
        self.specs = hardware.ServerSpecifications(bot=self)

        # Runs gc if the program is going to run out of memory
        if gc_clear:
            logger.warn(f"Automatic garbage collector enabled. Running it every {gc_sleep} sec.")
            self.loop.create_task(utils.auto_gc(self.specs, gc_sleep, gc_max_ram))

        # Synchronous clients for Sqlite3
        self.db = database.db()
        self.cursor = self.db.cursor()
        # Creating default guild table
        self.cursor.execute("CREATE TABLE IF NOT EXISTS guilds(guild_id INTEGER PRIMARY KEY, prefix TEXT, lang TEXT)")
        self.db.commit()

        # Loading all the cogs and extentions
        logger.log("Loading cogs...")
        _path = utils.convert_to_import_path(COGS_PATH)
        buildin_cogs = [f"{_path}.{cog}" for cog in BUILTIN_COGS]
        _path = utils.convert_to_import_path(self.extentions_path)
        extentions = []
        for extention in listdir(self.extentions_path):
            if extention in ("__pycache__",) or extention.endswith((".md",)): 
                continue
            if extention.endswith(".py"): 
                extention = extention[:-3]
            extentions.append(f"{_path}.{extention}")
        if extentions == []:
            logger.warn(f"No extention will load because folder '{self.extentions_path}' is empty.")
        for cog in buildin_cogs + extentions:
            try:
                self.load_extension(cog)
                continue
            except discord.ExtensionNotFound as e:
                if cog in buildin_cogs:
                    logger.error(f"Couldn't find cog '{cog}' wich is a builtin, the bot may not work as expected.", e)
                    continue
                error = e
            except ImportError as e:
                if cog in extentions:
                    logger.error(f"Couldn't import the necessary modules inside this extension. Try to install them if you didn't.", e)
                error = e
            except Exception as e:
                error = e
            logger.error(f"Couldn't load cog '{cog}'.", error)

        if not path.exists("./burgir.jpg"):
            logger.quiet("File 'burgir.jpg' is missing, why did you delete it ???")
            # Really ?! Why ???

        logger.log(f"Finished initialization : {len(self.languages)} languages and {len(self.plugins.values())} plugins for {len(self.cogs.values())} cogs." + \
                   f" Took {(perf_counter()-start_time)*1000:.2f} ms.")

    @property
    def plugins(self) -> dict[str, PluginCog]:
        """A read-only mapping of plugin name to PluginCog.

        Returns:
            dict[str, PluginCog]
        """
        plugins = {}
        for cog in self.cogs.values():
            if isinstance(cog, PluginCog):
                plugins[cog.plugin_name] = cog
        return plugins
    
    @property
    def uptime(self) -> hardware.Uptime:
        """The uptime of the bot.

        Returns:
            Uptime: An instance of `src.hardware.Uptime`.
        """
        return hardware.Uptime(self.init_time)
    
    @property
    def avg_processing_time(self) -> float:
        """The average processing time of the bot for a command.
        
        Returns:
            float: The average in ms.
        """
        if len_prs_tms:= len(self.process_times):
            return sum(self.process_times)/len_prs_tms*1000
        return 0

    def add_bot(self, cls: object) -> object:
        """Adds the bot to the class if it has the attribute `bot`. 

        Returns:
            Any: The instance of your object with the bot.
        """
        cls.bot = self
        return cls

    def add_language(self, language: str) -> None:
        """Adds a language to the bot.

        Args:
            language (str): Must be an language code like `en`, `de` or `fr`.

        Raises:
            TypeError: `language` isn't an str object.
        """
        if not isinstance(language, str):
            raise TypeError(f"'language' must be an 'str' object and not '{type(language).__name__}'.")
        if language not in self.languages:
            self.languages.append(language)
    
    def init_reddit(self, client_id: str, client_secret: str, username: str, password: str, *args, **kwargs) -> None:
        """Initializes the Reddit client.

        Args:
            client_id (str): The application id.
            client_secret (str): The application secret.
            user_name (str): The id of the account on which the application was created.
            password (str): The password of the account.
        """
        logger.log(f"Initializing Reddit client.")
        self.reddit = reddit.Reddit(loop=self.loop, client_secret=client_secret, password=password, username=username, client_id=client_id, *args, **kwargs)
        
    async def _perf_command(self, method) -> None:
        start_time = perf_counter()
        await method
        self.process_times.append(perf_counter()-start_time)
        self.invoked_commands += 1
        if len(self.process_times) > MAX_PROCESS_TIMES_LEN:
            self.process_times = self.process_times[1:]
    async def process_commands(self, message: discord.Message): await self._perf_command(super().process_commands(message))
    async def process_application_commands(self, interaction: discord.Interaction, auto_sync: bool | None = None):
        await self._perf_command(super().process_application_commands(interaction, auto_sync))

    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.content != after.content and before.created_at.timestamp() >= (datetime.utcnow()-timedelta(minutes=5)).timestamp():
            await self.process_commands(after)

    async def on_ready(self) -> None:
        if self.is_alive is None:
            self.project_owner = await self.get_or_fetch_user(SHIBZEL_ID)
            self.instance_owners = await gather(*[self.get_or_fetch_user(_id) for _id in self.owner_ids])
            logger.log("The following users are the owners of this instance : {0}.".format(", ".join(f"'{user}'" for user in self.instance_owners)))
            self.invite_bot_url = f"https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=8&scope=bot%20applications.commands"
            logger.log(f"Setting bot invitation link as '{self.invite_bot_url}'.")
        self.is_alive = True
        logger.log(f"Ready. Connected as '{self.user}' (ID : {self.user.id}).")

    async def on_resumed(self) -> None:
        self.is_alive = True

    async def on_disconnect(self) -> None:
        if self.is_alive != False:
            self.is_alive = False

    async def on_guild_join(self, guild: discord.Guild) -> None:
        logger.quiet(f"Joined guild '{guild.name}' (ID: {guild.id}).")

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        logger.quiet(f"Left guild '{guild.name}' (ID: {guild.id}). Goodbye.")

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        logger.error(f"Ignoring exception in {event_method}: \n{PStyles.ENDC}-> {format_exc()}")

    def _on_cog(self, method, *args, **kwargs) -> None:
        """Fixes a bug beacause using methods like loading must run twice."""
        try:
            method(*args, **kwargs)
        except AttributeError:
            method(*args, **kwargs)
    def load_extension(self, *args, **kwargs): self._on_cog(super().load_extension, *args, **kwargs)
    def unload_extension(self, *args, **kwargs): self._on_cog(super().unload_extension, *args, **kwargs)
    def reload_extension(self, *args, **kwargs): self._on_cog(super().reload_extension, *args, **kwargs)

    def run(self, token: str, command_input: bool = False, *args, **kwargs) -> None:
        """Runs the bot.

        Args:
            command_input (bool, optional): Accept command input from the user. Defaults to False.
        """
        try:
            if command_input:
                self.console = Console(self)
                self.console.start()
            super().run(token, *args, **kwargs)
        except Exception as e:
            # Closing everything and reraising error
            self.loop.create_task(self.close(e))

    async def close(self, error: Exception = None) -> None:
        """Closes the bot.

        Args:
            error (Exception, optional): The error which caused the bot to stop. Defaults to None.

        Raises:
            error: Reraised error, if there is one.
        """
        logger.error("Shibbot is being stopped, goodbye !", error)
        to_close = [self.specs.close(), super().close()]
        if self.reddit:
            to_close.append(self.reddit.close())
        await gather(*to_close)
        self.loop.close()
        self.db.close()
        if error: raise error

class PterodactylShibbot(Shibbot):
    """A subclass of `Shibbot` using the Pterodactyl API for hardware usage."""

    def __init__(self, ptero_url: str = None, ptero_token: str = None, ptero_server_id: str = None, ptero_refresh: float = 5.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.specs = hardware.ServerSpecifications(bot=self, using_ptero=True,
                                                        ptero_url=ptero_url, ptero_token=ptero_token, ptero_server_id=ptero_server_id, secs_looping=ptero_refresh)
        logger.quiet("Using the Pterodactyl API to get hardware usage.")