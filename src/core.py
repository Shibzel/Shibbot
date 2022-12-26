"""Shibbot's base."""
import discord
from discord.ext import bridge
import os
import time
import traceback
import asyncio


from . import database
from .utils import Logger, ServerSpecifications, auto_gc, Reddit
from .constants import COGS_PATH, SHIBZEL_ID
from .models import PluginCog
from .console import ConsoleThread


def bot_get_prefix(bot, ctx):
    return database.get_prefix(ctx)


class Shibbot(bridge.Bot):
    """Subclass of `bridge.Bot`, our little Shibbot :3."""

    def __init__(self, test_mode = False, instance_owners: list[int] = [],
                 gc_clear: bool = False, gc_sleep: float = 60.0, gc_max_ram: float = 80.0,
                 *args, **kwargs):
        Logger.log("Initializing Shibbot...")
        start_time = time.time()
        self.test_mode = test_mode
        if self.test_mode:
            Logger.warn("Test/beta mode is enabled.")
        self.is_alive = None
        self.languages = []
        self.reddit = None

        super().__init__(
            command_prefix=bot_get_prefix,
            owner_ids=[SHIBZEL_ID] if instance_owners == [] else instance_owners,
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
        self.specs = ServerSpecifications(bot=self)

        # Runs gc if the program is going to run out of memory
        if gc_clear:
            Logger.warn(f"Automatic garbage collector enabled. Running GC every {gc_sleep} sec.")
            self.loop.create_task(auto_gc(self.specs, gc_sleep, gc_max_ram))

        # Synchronous clients for Sqlite3
        self.db = database.db()
        self.cursor = self.db.cursor()
        # Creating default guild table
        self.cursor.execute("CREATE TABLE IF NOT EXISTS guilds(guild_id INTEGER PRIMARY KEY, prefix TEXT, lang TEXT)")
        self.db.commit()

        # Loading all the cogs
        Logger.log("Loading cogs...")
        path = COGS_PATH
        if path.startswith("./"):
            path = path[2:]
        files = os.listdir(path) # Getting all the file names in the cog folders
        treated_cogs = []
        for filename in files:
            if filename not in ("__pycache__",):
                cogname = filename
                if cogname.endswith(".py"):
                    cogname = cogname[:-3]
                try:
                    self.load_extension(f"{path.replace('/', '.')}.{cogname}")
                except Exception as e:
                    Logger.error(f"Could not load '{cogname}' cog.", e)
                treated_cogs.append(cogname)
        if treated_cogs == []:
            Logger.warn(f"No cog was loaded, because nothing was in '{COGS_PATH}'.")

        if not os.path.exists("./burgir.jpg"):
            Logger.warn("File 'burgir.jpg' is missing, why did you delete it ???")
            # Really ?! Why ???
        Logger.log(f"Finished initialization : {len(self.languages)} languages and {len(self.plugins.values())} plugins for {len(self.cogs.values())} cogs." + \
                   f" Took {time.time()-start_time:.2f} sec.")
      

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

    
    def init_reddit(self, client_secret: str, password: str, user_name: str, client_id:str, *args, **kwargs):
        """_summary_

        Args:
            client_secret (str): _description_
            password (str): _description_
            user_name (str): _description_
            client_id (str): _description_
        """
        self.reddit = Reddit(self.loop, client_secret, password, user_name, client_id, *args, **kwargs)


    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.content != after.content:
            await self.process_commands(after)


    async def on_ready(self) -> None:
        if self.is_alive is None:
            self.project_owner = await self.get_or_fetch_user(SHIBZEL_ID)
            self.instance_owners = await asyncio.gather(*[self.get_or_fetch_user(_id) for _id in self.owner_ids])
            owners = ", ".join([f"'{user}'" for user in self.instance_owners])
            Logger.log(f"The following users are the owners of this instance : {owners}.")
            self.invite_bot_url = f"https://discord.com/api/oauth2/authorize?client_id={super().user.id}&permissions=8&scope=bot%20applications.commands"
            Logger.log(f"Setting bot invitation link as '{self.invite_bot_url}'.")
        self.is_alive = True
        Logger.log(f"Ready. Connected as '{super().user}' (ID : {super().user.id}).")


    async def on_resumed(self) -> None:
        self.is_alive = True


    async def on_disconnect(self) -> None:
        if self.is_alive != False:
            self.is_alive = False


    async def on_guild_join(self, guild: discord.Guild) -> None:
        Logger.log(f"Joined guild '{guild.name}' (ID: {guild.id})")


    async def on_guild_remove(self, guild: discord.Guild) -> None:
        Logger.log(f"Left guild '{guild.name}' (ID: {guild.id})")


    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        Logger.error(f"Ignoring exception in {event_method}: \n-> {traceback.format_exc()}")


    def run(self, token: str, command_input: bool = False, *args, **kwargs) -> None:
        """Runs the bot.

        Args:
            command_input (bool, optional): Accept command input from the user. Defaults to False.
        """
        try:
            if command_input:
                self.console_thread = ConsoleThread(self)
                self.console_thread.start()
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
        Logger.error("Shibbot is being stopped, goodbye !", error)
        to_close = [self.specs.close(), super().close()]
        if self.reddit:
            to_close.append(self.reddit.close())
        await asyncio.gather(*to_close)
        self.loop.close()
        self.db.close()
        if error: raise error
        

class PterodactylShibbot(Shibbot):
    """A subclass of `Shibbot` using the Pterodactyl API for hardware usage."""

    def __init__(self, ptero_url: str = None, ptero_token: str = None, ptero_server_id: str = None, ptero_refresh: float = 5.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.specs = ServerSpecifications(bot=self, using_ptero=True,
                                                        ptero_url=ptero_url, ptero_token=ptero_token, ptero_server_id=ptero_server_id, secs_looping=ptero_refresh)
        Logger.warn("Using the Pterodactyl API to get hardware usage.")