import asyncio
import random

import discord
from discord.ext import commands, tasks

from utils import endswith
from bot import Shibbot


def setup(client):
    client.add_cog(BotEvents(client))


class BotEvents(commands.Cog):
    def __init__(self, client):
        self.client: Shibbot = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        pass  # Say hello

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(5.5)
        self.change_activity.start()

    @tasks.loop(seconds=30)
    async def change_activity(self):
        if random.choice((True, False)):
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name=random.choice(
                    [f"the version {self.client.version}",  # self.client.website_url,
                        f"over {len(self.client.guilds)} servers", f"over {len(self.client.users)} users", "/help"]
                )
            )
        else:
            activity = random.choice(
                [
                    discord.Activity(
                        type=discord.ActivityType.watching,
                        name=random.choice(
                            ["after the guy who stole my milk", "you.", "submissions on Reddit", "the end of the world", "ur mama",
                                "inside your soul", "to but rare fish", "mee6.xyz, nah i'm joking (don't have a website tho, that's sad :c)"]
                        )
                    ),
                    discord.Activity(
                        type=discord.ActivityType.listening,
                        name=random.choice(
                            ["Jetpack Joyride Main Theme", "Kahoot Lobby Music",
                                "goofy ahh sound - goofy ahh dj", "Rick Astley - Never Gonna Give You Up", "wenomechainsama"]
                        )
                    ),
                    discord.Game(
                        name=random.choice(
                            ["Sea of Shibbs", f"Five Nights at Doggo's {random.randint(1, 5)}", "Fortinaiti ila Babaji ?", "Amogus ඞ",
                             "ROBLOSS", "Shibapunk 2077", "HEE HEE HE HA", "Minecraft 2.0", "Shiba Horizon 5", "Portel 2"]
                        )
                    )
                ]
            )
        await self.client.change_presence(activity=activity)

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error):
        lang = self.client.fl(self.client.get_lang(ctx))
        if isinstance(error, commands.CommandOnCooldown):
            embed = ErrorEmbed(
                description=lang.CommandOnCooldown["description"].format(
                    secs=round(error.cooldown.get_retry_after(), 2)
                )
            )
            return await ctx.respond(
                embed=embed,
                delete_after=error.cooldown.per
            )
        else:
            print(type(error))

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        """Command invoked when an error occurs."""
        lang = self.client.fl(self.client.get_lang(ctx))
        time = None if self.client.test_mode else 20

        if isinstance(error, commands.PrivateMessageOnly):
            embed = ErrorEmbed(
                description=lang.PrivateMessageOnly["description"]
            )
        elif isinstance(error, commands.NoPrivateMessage):
            embed = ErrorEmbed(
                description=lang.NoPrivateMessage["description"]
            )
        elif isinstance(error, commands.NotOwner):
            embed = ErrorEmbed(
                description=lang.NotOwner["description"])
        elif isinstance(error, (commands.MemberNotFound, commands.UserNotFound)
                        ):
            embed = ErrorEmbed(
                description=lang.UserNotFound["description"])
        elif isinstance(error, commands.ChannelNotFound):
            embed = ErrorEmbed(
                description=lang.ChannelNotFound["description"]
            )
        if isinstance(error, commands.CommandOnCooldown):
            embed = ErrorEmbed(
                description=lang.CommandOnCooldown["description"].format(
                    secs=round(error.cooldown.get_retry_after(), 2)
                )
            )
            time = error.cooldown.per
        elif isinstance(error, commands.NSFWChannelRequired):
            embed = ErrorEmbed(
                description=lang.NSFWChannelRequired["description"].format(
                    channel=error.channel.mention)
            )
        elif isinstance(error, commands.MissingPermissions):
            for permission in error.missing_permissions:
                str_permission = permission.replace("_", " ")
                if permission == error.missing_permissions[0]:
                    permissions = f"`{str_permission}`"
                else:
                    permissions += f" and `{str_permission}`"
            embed = ErrorEmbed(
                description=lang.MissingPermissions["description"].format(
                    permissions=permissions)
            )
        elif isinstance(error, commands.BotMissingPermissions):
            embed = ErrorEmbed(
                description=lang.BotMissingPermissions["description"]
            )
        elif isinstance(error, commands.BadArgument):
            embed = ErrorEmbed(
                description=lang.BadArgument["description"]
            )
        elif isinstance(error, (commands.CommandNotFound, commands.CheckFailure)
                        ):
            return

        else:
            if self.client.test_mode:
                embed = discord.Embed(
                    title="Error",
                    description=f"Something went wrong :\n```{type(error).__name__}: {error}```",
                    color=discord.Color.red()
                )
            else:
                text = lang.CommandError
                embed = ErrorEmbed(
                    description=text["description"]
                )
                embed.set_footer(text=text["footer"].format(
                    owner=self.client.get_user(self.client.owner_id)
                )
                )

        try:
            dismiss_button = discord.ui.Button(
                style=discord.ButtonStyle.danger,
                label=lang.CommandError["dissmiss"],
                emoji="✖"
            )
            message: discord.Message = await ctx.reply(
                embed=discord.Embed(
                    description="⏳",
                    color=discord.Color.red()
                )
            )

            async def delete_message(interaction: discord.Interaction):
                await message.delete()
                reply_message = message.channel.get_partial_message(
                    message.reference.message_id)
                await reply_message.delete()
            dismiss_button.callback = delete_message
            view = discord.ui.View(dismiss_button)
            await message.edit(
                embed=embed,
                view=view,
                delete_after=time
            )
        except:
            print(f"[x] Unexpected error : {type(error).__name__}: {error}")


class ErrorEmbed(discord.Embed):
    def __init__(self, description):
        super().__init__(title="Oops...",
                         description="＞︿＜ "+description, color=discord.Color.red())
