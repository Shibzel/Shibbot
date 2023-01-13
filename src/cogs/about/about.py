import discord
from discord.ext import bridge, commands
from platform import python_version
from random import choice

from src import __version__ as version, __github__ as github_link, database
from src.core import Shibbot
from src.models import BaseCog, CustomView
from src.utils import get_description_localization, stringify_command_usage, get_language
from src.utils.hardware import Uptime
from src.constants import SERVER_INVITATION_LINK

from . import English, French


class About(BaseCog):
    def __init__(self, bot):
        self.bot: Shibbot = bot
        super().__init__(
            bot=bot,
            name={"en": "About", "fr": "A Propos"},
            description={"en": "About the bot.", "fr": "A propos du bot."},
            languages={"en": English, "fr": French}, emoji="📍"
        )

    @bridge.bridge_command(name="help", description="Shows help.", description_localizations={"fr": "Affiche de l'aide."})
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def show_help(self, ctx: bridge.BridgeApplicationContext):
        lang_code = await database.get_language(ctx)
        lang = get_language(self.languages, lang_code)

        TITLE = lang.SHOW_HELP_TITLE
        FOOTER = f"Shibbot v{version} | "
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
            embed.set_footer(text=FOOTER+choice(lang.SHOW_HELP_FOOTER_HOME))

            view = self.bot.add_bot(CustomView(select, bot_button, server_button, github_button, timeout=300, disable_on_timeout=True))
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
                    description=f"**{f'{cog.emoji} ' if cog.emoji else ''}{cog.get_name(lang_code)} :** {cog.get_description(lang_code) if cog.description else '...'}",
                    color=discord.Color.dark_gold())
                embed.set_footer(text=FOOTER+lang.SHOW_HELP_FOOTER)
                value = ""
                for command in cog.get_commands():
                    # Getting the command's description
                    command_description = get_description_localization(command, lang_code)
                    # Stringifying the command's options
                    value += f"• `{stringify_command_usage(command, lang_code)}` : {command_description if command_description else '...'}\n"
                embed.add_field(name=lang.SHOW_HELP_COMMANDS_FIELD_NAME, value=value if value != "" else "...")
                view = self.bot.add_bot(CustomView(select, timeout=300, disable_on_timeout=True))
            await interaction.response.edit_message(embed=embed, view=view)
        select.callback = callback

        # Setting up the home page
        embed = await get_home_page()
        await ctx.respond(embed=embed, view=view)

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
        await ctx.respond(embed=embed, view=self.bot.add_bot(CustomView(bot_button, server_button)))

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

    @bridge.bridge_command(name="uptime", description="Displays since when the bot has been online.",
                                          description_localizations={"fr" : "Affiche depuis quand le bot est en ligne."})
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def get_uptime(self, ctx: bridge.BridgeApplicationContext):
        lang = await self.get_lang(ctx)

        # TODO: Get the uptime of the bot
        uptime = 0
        if uptime > 90: emoji, color = "🟢", discord.Color.green()
        elif 75 > uptime >= 90: emoji, color = "🟠", discord.Color.orange()
        elif not uptime: emoji, color = "⚪", 0xffffff
        else: emoji, color = "🔴", discord.Color.red()

        ut = Uptime(self.bot.init_time)

        embed = discord.Embed(color=color)
        embed.add_field(name=lang.GET_UPTIME_FIELD2_NAME, value=lang.GET_UPTIME_FIELD2_VALUE.format(emoji=emoji, uptime=uptime))
        embed.add_field(name=lang.GET_UPTIME_FIELD1_NAME, value=lang.GET_UPTIME_FIELD1_VALUE.format(d=ut.days, h=ut.hours, m=ut.minutes, s=ut.seconds))

        await ctx.respond(embed=embed)

    @bridge.bridge_command(name="tip", description="Tip the creator of the bot.", description_localizations={"fr": "Faites un don au crétaeur du bot."})
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def gimme_money(self, ctx: bridge.BridgeApplicationContext):
        # TODO: Complete this command.
        await ctx.respond("Command not available yet.")