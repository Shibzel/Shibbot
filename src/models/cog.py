from discord import Cog
from discord.ext.bridge import BridgeApplicationContext

from .. import __version__
from ..utils import fl, get_language, Logger
from .. import database
from ..errors import PluginDisabledError, DeprecatedBotError


logger = Logger(__name__)

def deprecated(min_version: str, current_version: str):
    current_version, min_version = current_version.split("."), min_version.split(".")
    if current_version[0] == min_version[0]: # Major
        return current_version[1] < min_version[1] # Minor
    else:
        return False

class BaseCog(Cog):
    """This dumbass dev forgot to add a documentation."""

    def __init__(self, bot, name: dict | None = None, description: dict | None = None, languages: dict | None = None, emoji: str | None = None,
                 hidden: bool = False, author: str | None = None, min_version_supported: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot or getattr(self, "bot", None)
        
        if not isinstance(name, dict) and name is not None:
            raise TypeError("'name' must be a dict. Exemple : {'en': 'Name', 'fr': 'Nom'}.")
        self.name = name
        if not isinstance(name, dict) and name is not None:
            raise TypeError("'description' must be a dict. Exemple : {'en': 'This is a description.', 'fr': 'Ceci est une description'}.")
        self.description = description
        if languages:
            self.languages = languages
            for lang in self.languages.keys():
                self.bot.add_language(lang)
        self.emoji = emoji
        
        self.is_hidden = hidden
        self.author = author
        if min_version_supported and deprecated(min_version_supported, __version__):
            raise DeprecatedBotError(min_version_supported, type(self).__name__)

    async def cog_before_invoke(self, ctx: BridgeApplicationContext):
        guild_string = f" on guild '{ctx.guild}' (ID: {ctx.guild.id})" if ctx.guild else ""
        logger.quiet(f"User '{ctx.author}' (ID: {ctx.author.id}) is running the '{type(self).__name__}.{ctx.command}' command{guild_string}.")
        return await super().cog_before_invoke(ctx)

    def get_name(self, lang_code: str) -> str:
        return get_language(self.name, lang_code) if self.name else self.__name__

    def get_description(self, lang_code: str) -> str:
        return get_language(self.description, lang_code) if self.description else None

    def get_lang(self, ctx):
        return fl(ctx, self.languages)


class PluginCog(BaseCog):
    def __init__(self, plugin_name: str, guild_only: bool = False, *args, **kwargs):
        self.plugin_name = plugin_name
        self.guild_only = guild_only
        super().__init__(*args, **kwargs)
        self.bot.cursor.execute(f"CREATE TABLE IF NOT EXISTS {plugin_name}_plugin (guild_id INTERGER PRIMARY_KEY, enabled BOOLEAN)")
        self.bot.db.commit()
        
    async def is_enabled(self, ctx: BridgeApplicationContext):
        return await database.plugin_is_enabled(ctx, self.plugin_name, self.guild_only)

    async def cog_before_invoke(self, ctx: BridgeApplicationContext):
        if not await self.is_enabled(ctx):
            raise PluginDisabledError(self.plugin_name)
        return await super().cog_before_invoke(ctx)
