import discord
from discord.ext import bridge, commands
import asyncio

from src import Shibbot, database
from src.models import BaseCog, CustomView
from src.utils import get_language
from src.errors import NotInteractionOwner, MissingArgumentsError
from src.constants import LANGUAGES_FLAGS, LANGUAGES

from . import English, French


class Configuration(BaseCog):
    
    def __init__(self, bot):
        self.bot: Shibbot = bot
        super().__init__(
            bot=bot,
            name={"en": "Configuration", "fr": "Configuration"},
            description={"en": "Set of configuration commands.", "fr": "Commandes de configuration."},
            languages={"en": English, "fr": French}, emoji="🛠️"
        )


    @bridge.bridge_command(name="prefix", description="Changes the prefix.", description_localizations={"fr": "Change le préfixe."},
                           options=[discord.Option(required=True, name="prefix", description="The prefix you want to set.",
                                                                                 description_localizations={"fr": "Le préfixe que vous voulez définir."})])
    @bridge.has_permissions(administrator=True)
    @commands.cooldown(2, 10, commands.BucketType.member)
    @bridge.guild_only()
    async def change_prefix(self, ctx: bridge.BridgeApplicationContext, prefix: str = None):
        if not prefix:
            raise MissingArgumentsError(ctx.command)

        lang = await self.get_lang(ctx)
        prefix = prefix.lower().split(" ")[0]
        await database.change_prefix(self.bot, ctx.guild, prefix)
        embed = discord.Embed(title=lang.CHANGE_PREFIX_TITLE, description="✅ "+lang.CHANGE_PREFIX_DESCRIPTION.format(prefix=prefix), color=discord.Color.green())
        await ctx.respond(embed=embed)


    @bridge.bridge_command(name="language", aliases=["lang"], description="Changes the bot's language.", description_localizations={"fr": "Change le langage du bot."})
    @bridge.has_permissions(administrator=True)
    @commands.cooldown(2, 10, commands.BucketType.member)
    @bridge.guild_only()
    async def change_lang(self, ctx: bridge.BridgeApplicationContext):
        lang_code = await database.get_language(ctx)
        lang = get_language(self.languages, lang_code)

        select = discord.ui.Select(options=[discord.SelectOption(label=LANGUAGES[language].title(), emoji=LANGUAGES_FLAGS[language] if LANGUAGES_FLAGS.get(language) else "🏴",
                                                                default=language==lang_code, value=language) for language in self.bot.languages])
        async def callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                raise NotInteractionOwner(ctx.author, interaction.user)
            
            set_language = select.values[0]
            await database.change_language(self.bot, ctx.guild, set_language)
            lang = get_language(self.languages, set_language)
            embed = discord.Embed(title=lang.CHANGE_LANG_DONE_TITLE,
                                  description=lang.CHANGE_LANG_DONE_DESCRIPTION.format(language_flag=LANGUAGES_FLAGS[set_language] if LANGUAGES_FLAGS.get(set_language) else "🏴",
                                                                                       language=LANGUAGES[set_language].title()), color=discord.Color.dark_gold())
            view.disable_all_items()
            await interaction.response.edit_message(embed=embed, view=view)
        select.callback = callback
        view = self.bot.add_bot(CustomView(select, disable_on_timeout=True))
        embed = discord.Embed(title=lang.CHANGE_LANG_MENU_TITLE, description=lang.CHANGE_LANG_MENU_DESCRIPTION, color=discord.Color.dark_gold())
        await ctx.respond(embed=embed, view=view)


    @bridge.bridge_command(name="plugins", aliases=["plugin"], description="Enables or disables plugins.", description_localizations={"fr": "Active ou désactive des plugins."})
    @bridge.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.member)
    @bridge.guild_only()
    async def enable_plugins(self, ctx: bridge.BridgeApplicationContext):
        lang_code = await database.get_language(ctx)
        lang = get_language(self.languages, lang_code)

        select = discord.ui.Select(placeholder=lang.ENABLE_PLUGINS_PLACEHOLDER, min_values=0, max_values=None,
                                   options=[discord.SelectOption(label=plugin.get_name(lang_code), description=plugin.get_description(lang_code) if plugin.description else "...",
                                                                emoji=plugin.emoji, default=await database.plugin_is_enabled(ctx, plugin.plugin_name), value=plugin.plugin_name) 
                                                                for plugin in self.bot.plugins.values()])
        async def callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                raise NotInteractionOwner(ctx.author, interaction.user)
            
            await asyncio.gather(*[database.enable_plugin(ctx.guild, plugin.plugin_name, 1 if plugin.plugin_name in select.values else 0) for plugin in self.bot.plugins.values()])
            embed = discord.Embed(title=lang.ENABLE_PLUGIN_DONE_TITLE, description=lang.ENABLE_PLUGIN_DONE_DESCRIPTION, color=discord.Color.dark_gold())
            view.disable_all_items()
            await interaction.response.edit_message(embed=embed, view=view)
        select.callback = callback
        view = self.bot.add_bot(CustomView(select, disable_on_timeout=True))
        embed = discord.Embed(title=lang.ENABLE_PLUGIN_MENU_TITLE, description=lang.ENABLE_PLUGIN_MENU_DESCRIPTION, color=discord.Color.dark_gold())
        await ctx.respond(embed=embed, view=view)


    
