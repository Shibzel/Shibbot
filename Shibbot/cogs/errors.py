import discord
from discord.ext import commands

from bot import Shibbot


def setup(client):
    client.add_cog(Error(client))


class Error(commands.Cog):
    def __init__(self, client):
        self.client: Shibbot = client

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error):
        text = self.client.fl(await self.client.get_lang(ctx.guild)).on_command_error
        if isinstance(error, commands.CommandOnCooldown):
            embed = ErrorEmbed(
                description=text["CommandOnCooldown"]["description"].format(
                    secs=round(error.cooldown.get_retry_after(), 2)))
            return await ctx.respond(
                embed=embed,
                delete_after=error.cooldown.per)
        else:
            print(f"[x] Unexpected error : {type(error).__name__}: {error}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        """Command invoked when an error occurs."""
        text = self.client.fl(await self.client.get_lang(ctx.guild)).on_command_error
        time = None if self.client.test_mode else 20

        if isinstance(error, commands.PrivateMessageOnly):
            embed = ErrorEmbed(
                description=text["PrivateMessageOnly"]["description"])
        elif isinstance(error, commands.NoPrivateMessage):
            embed = ErrorEmbed(
                description=text["NoPrivateMessage"]["description"])
        elif isinstance(error, commands.NotOwner):
            embed = ErrorEmbed(
                description=text["NotOwner"]["description"])
        elif isinstance(error, (commands.MemberNotFound, commands.UserNotFound)):
            embed = ErrorEmbed(
                description=text["UserNotFound"]["description"])
        elif isinstance(error, commands.ChannelNotFound):
            embed = ErrorEmbed(
                description=text["textChannelNotFound"]["description"])
        if isinstance(error, commands.CommandOnCooldown):
            embed = ErrorEmbed(
                description=text["CommandOnCooldown"]["description"].format(
                    secs=round(error.cooldown.get_retry_after(), 2)))
            time = error.cooldown.per
        elif isinstance(error, commands.NSFWChannelRequired):
            embed = ErrorEmbed(
                description=text["NSFWChannelRequired"]["description"].format(
                    channel=error.channel.mention))
        elif isinstance(error, commands.MissingPermissions):
            embed_text = text["MissingPermissions"]
            for permission in error.missing_permissions:
                str_permission = permission.replace("_", " ")
                if permission == error.missing_permissions[0]:
                    permissions = f"`{str_permission}`"
                else:
                    permissions += f" {embed_text['and']} `{str_permission}`"
            embed = ErrorEmbed(
                description=embed_text["description"].format(
                    permissions=permissions))
        elif isinstance(error, commands.BotMissingPermissions):
            embed = ErrorEmbed(
                description=text["BotMissingPermissions"]["description"])
        elif isinstance(error, commands.BadArgument):
            embed = ErrorEmbed(
                description=text["BadArgument"]["description"])
        elif isinstance(error, (commands.CommandNotFound, commands.CheckFailure)):
            return

        else:
            if self.client.test_mode:
                embed = discord.Embed(
                    title="Error",
                    description=f"Something went wrong :\n```{type(error).__name__}: {error}```",
                    color=discord.Color.red())
            else:
                text = text["CommandError"]
                embed = ErrorEmbed(
                    description=text["description"])
                embed.set_footer(
                    text=text["footer"].format(
                        owner=self.client.get_user(self.client.owner_id)))

        try:
            dismiss_button = discord.ui.Button(
                style=discord.ButtonStyle.danger,
                label=text["CommandError"]["dissmiss"],
                emoji="✖")

            temp_embed = discord.Embed(
                description="⏳",
                color=discord.Color.red())
            message = await ctx.send(embed=temp_embed)

            async def delete_message(interaction: discord.Interaction):
                await message.delete()
                try:
                    reply_message = message.channel.get_partial_message(
                        message.reference.message_id)
                    await reply_message.delete()
                except:
                    pass
            dismiss_button.callback = delete_message
            view = discord.ui.View(dismiss_button)
            await message.edit(embed=embed, view=view, delete_after=time)
        except:
            print(f"[x] Unexpected error : {type(error).__name__}: {error}")


class ErrorEmbed(discord.Embed):
    def __init__(self, description):
        super().__init__(title="Oops...",
                         description="＞︿＜ "+description, color=discord.Color.red())
