import discord
from discord.ext import commands, bridge
import asyncio

from src.core import Shibbot
from src.utils import get_language, stringify_command_usage, send
from src.models import BaseCog, CustomView
from src.errors import NotInteractionOwner, PluginDisabledError, MissingArgumentsError

from .lang import French, English


class Events(BaseCog):
    def __init__(self, bot: Shibbot):
        self.bot = bot
        super().__init__(languages={"en": English(), "fr": French()}, hidden=True)
        self.cooldowns = []
        self.bot.set_error_handler(self)

    @discord.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        await self.handle_error(ctx, error)

    @discord.Cog.listener()
    async def on_command_error(self, ctx, error):
        await self.handle_error(ctx, error)

    async def add_user_cooldown(self, seconds: float, command_name: str, user_id: int):
        data = (command_name, user_id,)
        self.cooldowns.append(data)
        await asyncio.sleep(seconds)
        self.cooldowns.remove(data)

    def user_on_cooldown(self, command_name: str, user_id: int):
        return (command_name, user_id) in self.cooldowns

    async def handle_error(self, ctx: bridge.BridgeContext, error):
        if isinstance(error, commands.CommandOnCooldown):
            if self.user_on_cooldown(ctx.command.name, ctx.author.id):
                return

        db = self.bot.db
        lang_code = db.get_language(ctx.guild)
        lang: English = get_language(self.languages, lang_code)
        error_dict: dict[str, str] = lang.ON_COMMAND_ERROR
        time = None if self.bot.debug_mode else 20
        ephemeral = False

        if isinstance(error, commands.CommandOnCooldown):
            cooldown = error.cooldown.get_retry_after()
            time = error.cooldown.per
            ephemeral = True
            self.bot.loop.create_task(self.add_user_cooldown(
                cooldown, ctx.command.name, ctx.author.id))
            description = error_dict["CommandOnCooldown"].format(
                n_secs=round(cooldown, 2))
        elif isinstance(error, NotInteractionOwner):
            content = error_dict["NotInteractionOwner"].format(
                user_interacting=error.user_interacting.mention,
                interaction_owner=error.interaction_owner.mention)
            return await send(ctx, content=content, ephemeral=True)
        elif isinstance(error, PluginDisabledError):
            plugin_name = error.plugin_name
            for cog in self.bot.plugins.values():
                if cog.plugin_name == plugin_name:
                    plugin_name = cog.get_name(lang_code)
                    if emoji:= cog.emoji:
                        plugin_name = f"{emoji} {plugin_name}"
                    break
            return await send(ctx,
                              content=error_dict["PluginDisabledError"].format(plugin=plugin_name),
                              ephemeral=True)
        elif isinstance(error, MissingArgumentsError):
            description = error_dict["MissingArgumentsError"].format(
                command_usage=stringify_command_usage(error.command, lang_code))
            if message := error.error_case_msg:
                description += f" {message}"
        elif isinstance(error, commands.NSFWChannelRequired):
            description = error_dict["NSFWChannelRequired"].format(
                channel=error.channel.mention)
        elif isinstance(error, commands.MissingPermissions):
            description = error_dict["MissingPermissions"].format(permissions=" & ".join(
                permission.replace("_", " ") for permission in error.missing_permissions))
        elif isinstance(error, (commands.CommandNotFound, commands.CheckFailure,)):
            return
        else:
            error_name = type(error).__name__ if not isinstance(
                error, discord.Forbidden) else commands.BotMissingPermissions.__name__
            if error_name in error_dict:
                description = error_dict[error_name]
            else:
                name = getattr(ctx, "command", None) or repr(ctx)
                user = getattr(ctx, "author", None) or getattr(ctx, "user", None)
                error_message = f"Unexpected error with command '{name}' "
                if guild := getattr(ctx, "guild", None):
                    error_message += f"on guild {guild.name} (ID: {guild.id})."
                else:
                    error_message += f"with user {user} (ID: {user.id})."
                self.logger.error(error_message, error)
                description = error_dict["CommandError"].format(
                    owner=self.bot.get_user(self.bot.owner_id))

        view = None
        if not ephemeral:
            dismiss_button = discord.ui.Button(
                style=discord.ButtonStyle.danger, label=lang.DISSMISS_BUTTON, emoji="✖")

            async def delete_message(interaction: discord.Interaction):
                try:
                    await interaction.message.delete()
                    await interaction.message.reference.cached_message.delete()
                except (discord.Forbidden, discord.NotFound, AttributeError):
                    pass
            dismiss_button.callback = delete_message
            view = CustomView(dismiss_button, disable_on_timeout=True, bot=self.bot)

        embed = discord.Embed(title=lang.ON_COMMAND_ERROR_TITLE,
                              description="🔶 "+description, color=discord.Color.red())
        await send(ctx, embed=embed, view=view, delete_after=time, ephemeral=ephemeral)

def setup(bot):
    bot.add_cog(Events(bot))