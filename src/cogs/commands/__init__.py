import discord
from discord.ext import bridge, commands
from platform import python_version
import random

from src import __version__ as version, __github__ as github_link
from src.core import Shibbot
from src.models import BaseCog, CustomView
from src.utils import get_description_localization, stringify_command_usage, get_language
from src.constants import SERVER_INVITATION_LINK, LANGUAGES_FLAGS, LANGUAGES
from src.errors import NotInteractionOwner, MissingArgumentsError

from .lang import English, French, Shibberish


class BotsCommands(BaseCog):
    def __init__(self, bot: Shibbot):
        self.bot = bot
        super().__init__(
            name={
                "en": "Info & Config",
                "fr": "Infos & Config"
            },
            description={
                "en": "Everything about the bot.",
                "fr": "Tout ce qui concerne le bot."
            },
            languages={
                "en": English(),
                "fr": French(),
                "shibberish": Shibberish()
            },
            emoji="⚙️"
        )

    @bridge.bridge_command(
        name="help",
        description="Shows help.",
        description_localizations={"fr": "Affiche de l'aide."})
    @commands.cooldown(1, 7, commands.BucketType.user)
    @commands.cooldown(1, 15, commands.BucketType.channel)
    async def show_help(self, ctx: bridge.BridgeApplicationContext):
        db = self.bot.db
        _, prefix, lang_code, *_ = db.create_or_fetch_guild(self.bot, ctx.guild)
        lang: English = get_language(self.languages, lang_code)

        TITLE = lang.SHOW_HELP_TITLE
        FOOTER = f"Shibbot v{version} | "
        view = None

        # Listing all visible cogs and creating options accordingly
        options = [discord.SelectOption(label=lang.SHOW_HELP_OPTION_HOME_LABEL,
                                        emoji="🏡", value="home", default=True)]
        cogs: list[BaseCog] = []
        for cog in list(self.bot.cogs.values()):
            if isinstance(cog, BaseCog) and not cog.is_hidden and cog.get_commands():
                cogs.append(cog)
                options.append(
                    discord.SelectOption(label=cog.get_name(lang_code),
                                         description=cog.get_description(lang_code),
                                         emoji=cog.emoji, value=str(id(cog))))
        select = discord.ui.Select(options=options)

        bot_button = discord.ui.Button(label=lang.GET_INVITATIONS_INVITE_BOT_BUTTON,
                                       url=self.bot.invite_bot_url)
        server_button = discord.ui.Button(label=lang.GET_INVITATIONS_INVITE_SERVER_BUTTON,
                                          url=SERVER_INVITATION_LINK)
        github_button = discord.ui.Button(label="Github", url=github_link)

        async def get_home_page():
            """Returns an embed for the home page."""
            nonlocal view
            embed = discord.Embed(title=TITLE, description=lang.SHOW_HELP_DESCRIPTION,
                                  color=discord.Color.dark_gold())
            # embed.add_field(name=lang.SHOW_HELP_FIELD1_NAME, value=lang.SHOW_HELP_FIELD1_VALUE,
            #                 inline=True)
            embed.add_field(name=lang.SHOW_HELP_FIELD2_NAME,
                            value=lang.SHOW_HELP_FIELD2_VALUE.format(
                                github_link=github_link+"/releases/latest"))
            embed.add_field(name=lang.SHOW_HELP_FIELD3_NAME,
                            value=lang.SHOW_HELP_FIELD3_VALUE.format(
                                prefix=prefix),
                            inline=False)
            embed.set_thumbnail(url=self.bot.user.avatar)
            embed.set_footer(text=FOOTER+random.choice(lang.SHOW_HELP_FOOTER_HOME))

            view = CustomView(select, bot_button, server_button,
                              github_button, bot=self.bot, timeout=300)
            return embed

        async def callback(interaction: discord.Interaction):
            """The select bar's callback."""
            nonlocal view
            select_value = select.values[0]
            if select_value == "home":
                embed = await get_home_page()
                for option in options:
                    option.default = option.value == "home"
            else:
                for option in options:
                    option.default = select_value == option.value
                for _cog in cogs:
                    if select_value == str(id(_cog)):
                        cog = _cog
                        break
                embed = discord.Embed(
                    title=TITLE,
                    description=f"**{f'{cog.emoji} ' if cog.emoji else ''}{cog.get_name(lang_code)} :"
                                f"** {cog.get_description(lang_code) if cog.description else '...'}",
                    color=discord.Color.dark_gold())
                embed.set_footer(text=FOOTER+lang.SHOW_HELP_FOOTER)
                value = ""
                for command in cog.get_commands():
                    # Getting the command's description
                    command_description = get_description_localization(
                        command, lang_code)
                    # Stringifying the command's options
                    value += f"• `{stringify_command_usage(command, lang_code)}` :" + \
                             f" {command_description if command_description else '...'}\n"
                embed.add_field(name=lang.SHOW_HELP_COMMANDS_FIELD_NAME, value=value)
                view = CustomView(select, timeout=300, bot=self.bot)
            await interaction.response.edit_message(embed=embed, view=view)
        select.callback = callback

        # Setting up the home page
        embed = await get_home_page()
        await ctx.respond(embed=embed, view=view)

    @bridge.bridge_command(
        name="ping",
        description="Gets the bot's ping.",
        description_localizations={"fr": "Obtient le ping du bot."})
    @commands.cooldown(1, 7, commands.BucketType.default)
    async def ping(self, ctx: bridge.BridgeApplicationContext):
        lang: English = self.get_lang(ctx)
        embed = discord.Embed(
            title=lang.PING_EMBED_TITLE,
            description=lang.PING_EMBED_DESCRIPTION.format(
                ping=round(self.bot.latency*1000, 2),
                cpu=round(self.bot.specs.cpu_percentage, 2),
                ram=round(self.bot.specs.memory_percentage, 2)),
            color=discord.Color.dark_gold())
        await ctx.respond(embed=embed)

    @bridge.bridge_command(
        name="invite",
        aliases=["botinvite", "support"],
        description="Gets you the bot's invitation links.",
        description_localizations={"fr": "Vous obtient les liens d'invitation du bot."})
    @commands.cooldown(1, 7, commands.BucketType.default)
    async def get_invitations(self, ctx: bridge.BridgeApplicationContext):
        lang: English = self.get_lang(ctx)

        embed = discord.Embed(
            title=lang.GET_INVITATIONS_TITLE,
            description=lang.GET_INVITATIONS_DESCRIPTION,
            color=discord.Color.dark_gold())
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/955511076261347369/963461186756694096/happy_doggo.jpg")
        embed.set_footer(text=lang.GET_INVITATIONS_FOOTER)

        bot_button = discord.ui.Button(label=lang.GET_INVITATIONS_INVITE_BOT_BUTTON,
                                       url=self.bot.invite_bot_url)
        server_button = discord.ui.Button(label=lang.GET_INVITATIONS_INVITE_SERVER_BUTTON,
                                          url=SERVER_INVITATION_LINK)
        await ctx.respond(embed=embed, view=CustomView(bot_button, server_button, bot=self.bot))

    @bridge.bridge_command(
        name="botinfo",
        aliases=["about", "specs", "botspecs"],
        description="Gets informations about the bot.",
        description_localizations={"fr": "Obtiens des informartions sur le bot."})
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def get_infos(self, ctx: bridge.BridgeApplicationContext):
        lang: English = self.get_lang(ctx)

        embed = discord.Embed(color=discord.Color.dark_gold())
        embed.set_author(name=lang.GET_INFOS_TITLE.format(
            version=version), icon_url=self.bot.user.avatar)
        embed.add_field(inline=False, name=lang.GET_INFOS_FIELD1_NAME,
                        value=lang.GET_INFOS_FIELD1_DESCRIPTION.format(
                            n_servers=len(self.bot.guilds),
                            n_users=len(self.bot.users),
                            owner_github="https://github.com/Shibzel",
                            owner=self.bot.project_owner if self.bot.project_owner else "shibzel"))
        specs = self.bot.specs
        embed.add_field(name=lang.GET_INFOS_FIELD2_NAME,
                        value=lang.GET_INFOS_FIELD2_DESCRIPTION.format(
                            python_version=python_version(),
                            pycord_version=discord.__version__,
                            n_threads=specs.threads,
                            cpu_percent=round(specs.cpu_percentage, 2),
                            ram_usage=round(specs.memory_usage, 2),
                            n_ram=round(specs.max_memory, 2),
                            place=specs.location)
        )
        uptime = self.bot.uptime
        embed.add_field(name=lang.GET_INFOS_FIELD4_NAME,
                        value=lang.GET_INFOS_FIELD4_DESCRIPTION.format(
                            d=uptime.days, h=uptime.hours, m=uptime.minutes, s=uptime.seconds,
                            commands=self.bot.invoked_commands,
                            processing_time=round(
                                self.bot.avg_processing_time, 2),
                            members=max(len(guild.members) for guild in self.bot.guilds)))
        embed.add_field(name=lang.GET_INFOS_FIELD3_NAME,
                        value=lang.GET_INFOS_FIELD3_DESCRIPTION, inline=False)

        await ctx.respond(embed=embed)

    @bridge.bridge_command(
        name="prefix", 
        escription="Changes the prefix.",
        description_localizations={"fr": "Change le préfixe."},
        options=[
            discord.Option(
                required=True,
                name="prefix",
                description="The prefix you want to set.",
                description_localizations={"fr": "Le préfixe que vous voulez définir."})
        ])
    @bridge.has_permissions(administrator=True)
    @commands.cooldown(2, 10, commands.BucketType.guild)
    @bridge.guild_only()
    async def change_prefix(self, ctx: bridge.BridgeApplicationContext, prefix: str = None):
        if not prefix:
            raise MissingArgumentsError(ctx.command)

        db = self.bot.db
        lang = get_language(self.languages, db.get_language(ctx.guild))
        prefix = prefix.lower().split(" ")[0]
        db.change_prefix(self.bot, ctx.guild, prefix)
        embed = discord.Embed(title=lang.CHANGE_PREFIX_TITLE, description="✅ " +
                              lang.CHANGE_PREFIX_DESCRIPTION.format(prefix=prefix), color=discord.Color.green())
        await ctx.respond(embed=embed)

    @bridge.bridge_command(
        name="lang",
        aliases=["language"],
        description="Changes the bot's language.",
        description_localizations={"fr": "Change le langage du bot."})
    @bridge.has_permissions(administrator=True)
    @commands.cooldown(2, 10, commands.BucketType.guild)
    @bridge.guild_only()
    async def change_lang(self, ctx: bridge.BridgeApplicationContext):
        db = self.bot.db
        lang_code = db.get_language(ctx.guild)
        lang: English = get_language(self.languages, lang_code)

        select = discord.ui.Select(options=[discord.SelectOption(
            label=LANGUAGES[language].title(),
            emoji=LANGUAGES_FLAGS[language] if LANGUAGES_FLAGS.get(
                language) else "🏴",
            default=language == lang_code, value=language) for language in self.bot.languages])

        async def callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                raise NotInteractionOwner(ctx.author, interaction.user)

            set_language = select.values[0]
            db = self.bot.db
            db.change_language(self.bot, ctx.guild, set_language)
            lang = get_language(self.languages, set_language)
            embed = discord.Embed(
                title=lang.CHANGE_LANG_DONE_TITLE,
                description=lang.CHANGE_LANG_DONE_DESCRIPTION.format(
                    language_flag=LANGUAGES_FLAGS[set_language] if LANGUAGES_FLAGS.get(
                        set_language) else "🏴",
                    language=LANGUAGES[set_language].title()), color=discord.Color.dark_gold())
            view.disable_all_items()
            await interaction.response.edit_message(embed=embed, view=view)
        select.callback = callback
        view = CustomView(select, bot=self.bot)
        embed = discord.Embed(title=lang.CHANGE_LANG_MENU_TITLE,
                              description=lang.CHANGE_LANG_MENU_DESCRIPTION,
                              color=discord.Color.dark_gold())
        await ctx.respond(embed=embed, view=view)

    @bridge.bridge_command(
        name="plugins", aliases=["plugin"],
        description="Enables or disables plugins.",
        description_localizations={"fr": "Active ou désactive des plugins."})
    @bridge.has_permissions(administrator=True)
    @commands.cooldown(1, 7, commands.BucketType.guild)
    @bridge.guild_only()
    async def enable_plugins(self, ctx: bridge.BridgeApplicationContext):
        db = self.bot.db
        lang_code = db.get_language(ctx.guild)
        lang: English = get_language(self.languages, lang_code)

        options = [discord.SelectOption(
            label=plugin.get_name(lang_code),
            description=plugin.get_description(
                lang_code) if plugin.description else "...",
            emoji=plugin.emoji, default=db.plugin_is_enabled(ctx.guild, plugin.plugin_name),
            value=plugin.plugin_name)
            for plugin in self.bot.plugins.values()]
        select = discord.ui.Select(placeholder=lang.ENABLE_PLUGINS_PLACEHOLDER,
                                   min_values=0, max_values=len(options), options=options)

        async def callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                raise NotInteractionOwner(ctx.author, interaction.user)

            db = self.bot.db
            mapping = {
                plugin.plugin_name: (plugin.plugin_name in select.values)
                for plugin in self.bot.plugins.values()
            }
            db.bulk_enable_plugin(ctx.guild, mapping)
            embed = discord.Embed(title=lang.ENABLE_PLUGIN_DONE_TITLE,
                                  description=lang.ENABLE_PLUGIN_DONE_DESCRIPTION,
                                  color=discord.Color.dark_gold())
            for option in options:
                option.default = option.value in select.values
            view.disable_all_items()
            await interaction.response.edit_message(embed=embed, view=view)
        select.callback = callback
        view = CustomView(select, bot=self.bot)
        embed = discord.Embed(title=lang.ENABLE_PLUGIN_MENU_TITLE,
                              description=lang.ENABLE_PLUGIN_MENU_DESCRIPTION,
                              color=discord.Color.dark_gold())
        await ctx.respond(embed=embed, view=view)

def setup(bot):
    bot.add_cog(BotsCommands(bot))