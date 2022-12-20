"""Shibbot's base."""
# The Pycord module, an (maintained) API wrapper that we will use for this bot.
# There is some differences with discord.py, if you're not familiar with this fork see their documentation at https://docs.pycord.dev/
import discord
from discord.ext import bridge
import os
import time
import traceback
import threading

from . import database
from .utils import Logger, ServerSpecifications, auto_gc
from .constants import COGS_PATH, SHIBZEL_ID
from .models import PluginCog, CustomView


def bot_get_prefix(bot, ctx):
    return database.get_prefix(ctx)


class Shibbot(bridge.Bot):
    """Subclass of `bridge.Bot`, our little Shibbot :3."""

    def __init__(self, test_mode = False, instance_owners: list[int] = [], gc_clear: bool = True, *args, **kwargs):
        Logger.log("Initializing Shibbot...")
        start_time = time.time()
        self.test_mode = test_mode
        if self.test_mode:
            Logger.warn("Test/beta mode is enabled.")
        self.is_alive = None
        self.languages = []
        
        owners = [SHIBZEL_ID] if instance_owners == [] else instance_owners
        super().__init__(
            command_prefix=bot_get_prefix,
            owner_ids=owners,
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
        self.specs = ServerSpecifications(self, self.loop, secs_looping=5)

        # Runs gc if the program is going to run out of memory
        sleep = 60
        if gc_clear:
            Logger.warn(f"Automatic garbage collector enabled. Running GC every {sleep} sec.")
            self.loop.create_task(auto_gc(self.specs, sleep,))

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
        """A mapping of plugin name to PluginCog."""
        plugins = {}
        for cog in self.cogs.values():
            if isinstance(cog, PluginCog):
                plugins[cog.plugin_name] = cog
        return plugins


    def add_bot(self, view):
        view.bot = self
        return view


    def add_language(self, language: str) -> None:
        """Adds a languge to the bot."""
        if not isinstance(language, str):
            raise TypeError(f"'language' must be an 'str' object and not '{type(language).__name__}'.")
        if language not in self.languages:
            self.languages.append(language)


    async def on_ready(self):
        """Runs when the bot has successfully connected to Discord API."""
        if self.is_alive is None:
            self.project_owner = self.get_user(SHIBZEL_ID)
            self.instance_owners = [self.get_user(_id) for _id in self.owner_ids]
            owners = ", ".join([f"'{user}'" for user in self.instance_owners])
            Logger.log(f"The following users are the owners of this instance : {owners}.")
            self.invite_bot_url = f"https://discord.com/api/oauth2/authorize?client_id={super().user.id}&permissions=8&scope=bot%20applications.commands"
            Logger.log(f"Setting bot invitation link as '{self.invite_bot_url}'.")
        self.is_alive = True
        Logger.log(f"Ready. Connected as '{super().user}' (ID : {super().user.id}).")


    async def on_resumed(self):
        self.is_alive = True
        time_took = time.time() - self.time_disconnected
        Logger.log(f"Resumed (disconnected for {time_took:.2f} sec).")


    async def on_disconnect(self):
        if self.is_alive != False:
            self.time_disconnected = time.time()
            self.is_alive = False
            Logger.warn("Disconnected.")


    async def on_guild_join(self, guild: discord.Guild):
        """Triggered when the bot joins a guild"""
        Logger.log(f"Joined guild '{guild.name}' (ID: {guild.id})")


    async def on_guild_remove(self, guild: discord.Guild):
        """Triggered when the bot leaves a guild."""
        Logger.log(f"Left guild '{guild.name}' (ID: {guild.id})")


    async def on_error(self, event_method: str, *args, **kwargs):
        Logger.error(f"Ignoring exception in {event_method}: \n-> {traceback.format_exc()}")


    def run(self, *args, **kwargs):
        """Runs the bot."""
        try:
            super().run(*args, **kwargs)
        except Exception as e:
            Logger.error("Uh oh, that's lame :/ Shibbot crashed.", e)
            self.db.close()
            Logger.end()
        
