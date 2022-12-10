import discord
from discord.ext import bridge, commands
from platform import python_version
import asyncio

from src import (
    Shibbot, BaseCog, database,
    LANGUAGES, LANGUAGES_FLAGS,
    __version__ as version, __github__ as github_link,
    get_description_localization, stringify_command_usage, get_language,
)
from src.errors import *
from .lang.en import English
from .lang.fr import French


SERVER_INVITATION_LINK = "https://discord.gg/TZNWfJmPwj"


def setup(bot):
    bot.add_cog(ConfigCog(bot))


class ConfigCog(BaseCog):
    
    def __init__(self, bot):
        self.bot: Shibbot = bot
        super().__init__(
            bot=bot,
            name={"en": "Info & Config", "fr": "Infos & Configuration"},
            description={"en": "Set of configuration and help commands.", "fr": "Commandes de configuration et d'aide."},
            languages={"en": English, "fr": French}, emoji="🛠️"
        )


    @bridge.bridge_command(name="ping", description="Gets the bot's ping.", description_localizations={"fr": "Obtient le ping du bot."})
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def ping(self, ctx: bridge.BridgeApplicationContext):
        lang = await self.get_lang(ctx)
        embed = discord.Embed(
            title="🏓 "+lang.PING_EMBED_TITLE,
            description=lang.PING_EMBED_DESCRIPTION.format(
                ping=round(self.bot.latency*1000, 2),
                cpu=round(self.bot.specs.cpu_percentage, 2),
                ram=round(self.bot.specs.memory_usage/self.bot.specs.max_memory*100, 2)),
            color=discord.Color.dark_gold())
        await ctx.respond(embed=embed)


    @bridge.bridge_command(name="help", description="Shows help.", description_localizations={"fr": "Affiche de l'aide."})
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def show_help(self, ctx: bridge.BridgeApplicationContext):
        lang_code = await database.get_language(ctx)
        lang = get_language(self.languages, lang_code)

        TITLE = lang.SHOW_HELP_TITLE
        FOOTER = f"Shibbot v{version} | "+lang.SHOW_HELP_FOOTER
        view = None

        # Listing all visible cogs and creating options accordingly
        options = [discord.SelectOption(label=lang.SHOW_HELP_OPTION_HOME_LABEL, emoji="🏡", value="home", default=True)]
        cogs: list[BaseCog] = []
        for cog in list(self.bot.cogs.values()):
            if not getattr(cog, "is_hidden", True) and isinstance(cog, BaseCog):
                cogs.append(cog)
                options.append(discord.SelectOption(label=cog.get_name(lang_code), description=cog.get_description(lang_code),
                                                    emoji=cog.emoji, value=str(id(cog))))
        select = discord.ui.Select(options=options)

        bot_button = discord.ui.Button(label=lang.GET_INVITATIONS_INVITE_BOT_BUTTON, url=self.bot.invite_bot_url)
        server_button = discord.ui.Button(label=lang.GET_INVITATIONS_INVITE_SERVER_BUTTON, url=SERVER_INVITATION_LINK)
        github_button = discord.ui.Button(label="Github", url=github_link)
        async def get_home_page():
            """Returns an embed for the home page."""
            nonlocal view
            embed = discord.Embed(title=TITLE, description=lang.SHOW_HELP_DESCRIPTION, color=discord.Color.dark_gold())
            embed.add_field(name=lang.SHOW_HELP_FIELD1_NAME, value=lang.SHOW_HELP_FIELD1_VALUE, inline=True)
            embed.add_field(name=lang.SHOW_HELP_FIELD2_NAME, value=lang.SHOW_HELP_FIELD2_VALUE.format(github_link=github_link+"/realeases/latest"), inline=True)
            embed.add_field(name=lang.SHOW_HELP_FIELD3_NAME, value=lang.SHOW_HELP_FIELD3_VALUE.format(prefix=await database.get_prefix(ctx)), inline=False)
            embed.set_thumbnail(url=self.bot.user.avatar)
            embed.set_footer(text=FOOTER)

            view = discord.ui.View(select, bot_button, server_button, github_button, disable_on_timeout=True)
            return embed

        async def callback(interaction: discord.Interaction):
            """The select bar's callback."""
            if interaction.user != ctx.author:
                raise NotInteractionOwner(ctx.author, interaction.user)

            nonlocal view
            select_value = select.values[0]
            if select_value == "home":
                embed = await get_home_page()
                for option in options:
                    option.default = option.value == "home"
            else:
                for option in options:
                    option.default = select_value == option.value
                for cog in cogs:
                    if select_value == str(id(cog)):
                        cog = cog
                        break
                embed = discord.Embed(
                    title=TITLE,
                    description=f"**{f'{cog.emoji} ' if cog.emoji else ''}{cog.get_name(lang_code)} :** {cog.get_description(lang_code) if cog.description else '...'}",
                    color=discord.Color.dark_gold())
                embed.set_footer(text=FOOTER)
                value = ""
                for command in cog.get_commands():
                    # Getting the command's description
                    command_description = get_description_localization(command, lang_code)
                    # Stringifying the command's options
                    value += f"• `{stringify_command_usage(command, lang_code)}` : {command_description if command_description else '...'}\n"
                embed.add_field(name=lang.SHOW_HELP_COMMANDS_FIELD_NAME, value=value)
                view = discord.ui.View(select, disable_on_timeout=True)
            await interaction.response.edit_message(embed=embed, view=view)
        select.callback = callback

        # Setting up the home page
        embed = await get_home_page()
        await ctx.respond(embed=embed, view=view)


    @bridge.bridge_command(name="invite", aliases=["botinvite", "support"], description="Gets you the bot's invitation links.", 
                                                                            description_localizations={"fr": "Vous obtient les liens d'invitation du bot."})
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def get_invitations(self, ctx: bridge.BridgeApplicationContext):
        lang = await self.get_lang(ctx)

        embed = discord.Embed(
            title=lang.GET_INVITATIONS_TITLE,
            description=lang.GET_INVITATIONS_DESCRIPTION,
            color=discord.Color.dark_gold())
        embed.set_image(url="https://cdn.discordapp.com/attachments/955511076261347369/963461186756694096/happy_doggo.jpg")
        embed.set_footer(text=lang.GET_INVITATIONS_FOOTER)
        
        bot_button = discord.ui.Button(label=lang.GET_INVITATIONS_INVITE_BOT_BUTTON, url=self.bot.invite_bot_url)
        server_button = discord.ui.Button(label=lang.GET_INVITATIONS_INVITE_SERVER_BUTTON, url=SERVER_INVITATION_LINK)
        await ctx.respond(embed=embed, view=discord.ui.View(bot_button, server_button))


    @bridge.bridge_command(name="botinfo", aliases=["about", "specs", "botspecs"], description="Gets informations about the bot.",
                                                                                   description_localizations={"fr" : "Obtiens des informartions sur le bot."})
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def get_infos(self, ctx: bridge.BridgeApplicationContext):
        lang = await self.get_lang(ctx)

        embed = discord.Embed(color=discord.Color.dark_gold())
        embed.set_author(name=lang.GET_INFOS_TITLE.format(version=version), icon_url=self.bot.user.avatar)
        embed.add_field(name=lang.GET_INFOS_FIELD1_NAME,
                        value=lang.GET_INFOS_FIELD1_DESCRIPTION.format(n_servers=len(self.bot.guilds),
                                                                       n_users=len(self.bot.users),
                                                                       owner_github="https://github.com/Shibzel",
                                                                       owner=self.bot.project_owner if self.bot.project_owner else "Shibzel#1873"))
        specs = self.bot.specs
        embed.add_field(name=lang.GET_INFOS_FIELD2_NAME,
                        value=lang.GET_INFOS_FIELD2_DESCRIPTION.format(python_version=python_version(),
                                                                       pycord_version=discord.__version__,
                                                                       n_threads=specs.threads,
                                                                       cpu_percent=round(specs.cpu_percentage, 2),
                                                                       ram_usage=round(specs.memory_usage, 2),
                                                                       n_ram=round(specs.max_memory, 2),
                                                                       place=specs.location))
        embed.add_field(name=lang.GET_INFOS_FIELD3_NAME, value=lang.GET_INFOS_FIELD3_DESCRIPTION, inline=False)

        await ctx.respond(embed=embed)


    @bridge.bridge_command(name="prefix", description="Changes the prefix.", description_localizations={"fr": "Change le préfixe."},
                           options=[discord.Option(name="prefix", description="The prefix you want to set.",
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
        embed = discord.Embed(title=lang.CHANGE_PREFIX_TITLE, description="✅ " + lang.CHANGE_PREFIX_DESCRIPTION.format(prefix=prefix), color=discord.Color.green())
        await ctx.respond(embed=embed)


    @bridge.bridge_command(name="language", aliases=["lang"], description="Changes the bot's language.", description_localizations={"fr": "Change le langage du bot."})
    @bridge.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.member)
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
            embed = discord.Embed(title=lang.CHANGE_LANG_DONE_TITLE,
                                  description=lang.CHANGE_LANG_DONE_DESCRIPTION.format(language_flag=LANGUAGES_FLAGS[set_language] if LANGUAGES_FLAGS.get(set_language) else "🏴",
                                                                                       language=LANGUAGES[set_language].title()), color=discord.Color.dark_gold())
            view.disable_all_items()
            await interaction.response.edit_message(embed=embed, view=view)
        select.callback = callback
        view = discord.ui.View(select, disable_on_timeout=True)
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
        view = discord.ui.View(select, disable_on_timeout=True)
        embed = discord.Embed(title=lang.ENABLE_PLUGIN_MENU_TITLE, description=lang.ENABLE_PLUGIN_MENU_DESCRIPTION, color=discord.Color.dark_gold())
        await ctx.respond(embed=embed, view=view)


    @bridge.bridge_command(name="tip", description="Tip the creator of the bot.", description_localizations={"fr": "Faites un don au crétaeur du bot."})
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def gimme_money(self, ctx: bridge.BridgeApplicationContext):
        return




    