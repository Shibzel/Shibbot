from discord import Cog, SlashCommand
from discord.ext import bridge, commands
from asyncio import sleep as async_sleep

from .. import __version__
from ..utils import fl, get_language
from .. import database
from ..logging import Logger
from ..errors import PluginDisabledError, DeprecatedBotError, PluginWithSameNameError


logger = Logger(__name__)

def version_deprecated(min_version: str, current_version: str):
    current_version, min_version = current_version.split("."), min_version.split(".")
    if current_version[0] == min_version[0]: # Major
        return current_version[1] < min_version[1] # Minor
    else:
        return False

class BaseCog(Cog):
    def __init__(self, bot = None, name: dict | None = None, description: dict | None = None, languages: dict | None = None, emoji: str | None = None,
                 hidden: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = getattr(self, "bot", None) or bot
        if self.bot is None:
            raise TypeError(f"{self.__name__} missing required argument: 'bot'.")
        
        if not isinstance(name, dict) and name is not None:
            raise TypeError("'name' must be a dict. Exemple : {'en': 'Name', 'fr': 'Nom'}.")
        self.name = name
        if not isinstance(name, dict) and name is not None:
            raise TypeError("'description' must be a dict. Exemple : {'en': 'This is a description.', 'fr': 'Ceci est une description'}.")
        self.description = description
        if languages:
            self.languages = languages
            for lang in self.languages:
                self.bot.add_language(lang)
        self.emoji = emoji
        self.is_hidden = hidden
        
        self._when_fully_ready_called = False
        if self.bot.is_alive:
            self.bot.loop.create_task(self.when_fully_ready())
            self._when_fully_ready_called = True

    @Cog.listener("on_ready")
    async def _on_ready(self):
        if not self._when_fully_ready_called:
            await self.when_fully_ready()
            self._when_fully_ready_called = True
    async def when_fully_ready(self) -> None:
        """Similar to `on_connect`, this method is called when the cog is reloaded or when the bot is ready for the first time."""
        pass
    
    def get_name(self, lang_code: str) -> str:
        return get_language(self.name, lang_code) if self.name else self.__name__

    def get_description(self, lang_code: str) -> str:
        return get_language(self.description, lang_code) if self.description else None

    def get_lang(self, ctx) -> object:
        return fl(ctx, self.languages)
    
    def get_commands(self) -> list[SlashCommand | commands.Command]:
        slash_commands = [c for c in self.__cog_commands__ if isinstance(c, SlashCommand)]
        prefixed_commands = [c for c in self.__cog_commands__ if isinstance(c, commands.Command)]
        for slash_command in slash_commands:          
            for prefixed_command in prefixed_commands:
                if slash_command.name == prefixed_command.name:
                    prefixed_commands.remove(prefixed_command)
        return slash_commands + prefixed_commands
    
class PluginCog(BaseCog):
    def __init__(self, plugin_name: str, guild_only: bool = False, *args, **kwargs):
        self.plugin_name = plugin_name
        self.guild_only = guild_only
        super().__init__(*args, **kwargs)
        logger.debug(f"Creating '{plugin_name}_plugin' table in database.")
        self.bot.cursor.execute(f"CREATE TABLE IF NOT EXISTS {plugin_name}_plugin (guild_id INTERGER PRIMARY_KEY, enabled BOOLEAN)")
        self.bot.db.commit()
        
    async def is_enabled(self, ctx: bridge.BridgeApplicationContext):
        return await database.plugin_is_enabled(ctx, self.plugin_name, self.guild_only)

    async def cog_before_invoke(self, ctx: bridge.BridgeApplicationContext):
        if not await self.is_enabled(ctx):
            raise PluginDisabledError(self.plugin_name)
        return await super().cog_before_invoke(ctx)

class Extension(BaseCog):
    def __init__(self, author: str | None = None, min_version_supported: str = None, *args, **kwargs):
        self.author = author
        if min_version_supported and version_deprecated(min_version_supported, __version__):
            raise DeprecatedBotError(min_version_supported, type(self).__name__)
        super().__init__(*args, **kwargs)

class PluginExtension(PluginCog):
    def __init__(self, plugin_name: str, author: str | None = None, min_version_supported: str = None, *args, **kwargs):
        for cog in [plugin for plugin in self.bot.cogs.values() if isinstance(plugin, PluginCog)]:
            if cog.plugin_name == plugin_name:
                self.plugin_name = plugin_name
                raise PluginWithSameNameError(self, cog)
            
        self.author = author
        if min_version_supported and version_deprecated(min_version_supported, __version__):
            raise DeprecatedBotError(min_version_supported, type(self).__name__)
        super().__init__(plugin_name, *args, **kwargs)