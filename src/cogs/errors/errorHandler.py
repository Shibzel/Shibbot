import discord
from discord.ext import commands, bridge
from asyncio import sleep as async_sleep

from src import database
from src.core import Shibbot
from src.utils import get_language, stringify_command_usage
from src.logging import Logger
from src.models import BaseCog, CustomView
from src.errors import NotInteractionOwner, PluginDisabledError, MissingArgumentsError

from . import French, English


logger = Logger(__name__)

class ErrorHandler(BaseCog):
    
    def __init__(self, bot):
        self.bot: Shibbot = bot
        super().__init__(bot=bot, languages={"en": English, "fr": French}, hidden=True)
        self.cooldowns = []

    async def add_user_cooldown(self, seconds: float, command_name: str, user_id: int):
        data = (command_name, user_id,)
        self.cooldowns.append(data)
        await async_sleep(seconds)
        self.cooldowns.remove(data)

    def user_on_cooldown(self, command_name: str, user_id: int):
        return (command_name, user_id) in self.cooldowns

    async def handle_error(self, ctx: bridge.BridgeApplicationContext, error):
        logger.debug(f"Handling error : {type(error).__name__}: {str(error)}")
        if isinstance(error, commands.CommandOnCooldown) and self.user_on_cooldown(ctx.command.name, ctx.author.id):
            return

        lang_code = await database.get_language(ctx)
        lang = get_language(self.languages, lang_code)
        error_dict: dict[str, str] = lang.ON_COMMAND_ERROR
        time = None if self.bot.debug_mode else 20
        ephemeral = False

        if isinstance(error, commands.CommandOnCooldown):
            cooldown = error.cooldown.get_retry_after()
            time = error.cooldown.per
            ephemeral = True
            self.bot.loop.create_task(self.add_user_cooldown(cooldown, ctx.command.name, ctx.author.id))
            description = error_dict["CommandOnCooldown"].format(n_secs=round(cooldown, 2))
        elif isinstance(error, NotInteractionOwner):
            content = error_dict["NotInteractionOwner"].format(user_interacting=error.user_interacting.mention, interaction_owner=error.interaction_owner.mention)
            return await ctx.reply(content=content, ephemeral=True)
        elif isinstance(error, PluginDisabledError):
            return await ctx.respond(content=error_dict["PluginDisabledError"].format(plugin=error.plugin_name), ephemeral=True)
        elif isinstance(error, MissingArgumentsError):
            description = error_dict["MissingArgumentsError"].format(command_usage=stringify_command_usage(error.command, lang_code))
        elif isinstance(error, commands.NSFWChannelRequired):
            description = error_dict["NSFWChannelRequired"].format(channel=error.channel.mention)
        elif isinstance(error, commands.MissingPermissions):
            description = error_dict["MissingPermissions"].format(permissions=" & ".join(permission.replace("_", " ") for permission in error.missing_permissions))
        elif isinstance(error, (commands.CommandNotFound, commands.CheckFailure)):
            return
        else:
            error_name = type(error).__name__
            if error_name in error_dict:
                description = error_dict[error_name]
            else:
                error_message = f"Unexpected error with command '{ctx.command.name}' "
                if guild:= ctx.guild:
                    error_message += f"on guild {guild.name} (ID: {guild.id})."
                else:
                    error_message += f"with user {ctx.author} (ID: {ctx.author.id})."
                logger.error(error_message, error)
                description = error_dict["CommandError"].format(owner=self.bot.get_user(self.bot.owner_id))

        dismiss_button = discord.ui.Button(style=discord.ButtonStyle.danger, label=lang.DISSMISS_BUTTON, emoji="✖")
        async def delete_message(interaction: discord.Interaction):
            try:
                await interaction.message.delete()
                await interaction.message.reference.cached_message.delete()
            except (discord.Forbidden, discord.NotFound, AttributeError):
                pass
        dismiss_button.callback = delete_message
        view = self.bot.add_bot(CustomView(dismiss_button, disable_on_timeout=True))

        embed = discord.Embed(title=lang.ON_COMMAND_ERROR_TITLE, description="🔶 "+description, color=discord.Color.red())
        await ctx.respond(embed=embed, view=view, delete_after=time, ephemeral=ephemeral)
    @discord.Cog.listener()
    async def on_application_command_error(self, ctx, error): await self.handle_error(ctx, error)
    @discord.Cog.listener()
    async def on_command_error(self, ctx, error): await self.handle_error(ctx, error)
