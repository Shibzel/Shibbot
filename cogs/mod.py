import datetime
import asyncio
import datetime

import discord
from discord.ext import commands, tasks

from utils import remove_chars
from bot import Shibbot, __version__


client = None


def setup(_client):
    global client
    client = _client
    client.add_cog(Mod(client))


class Duration:
    def __init__(self, _datetime, raw_time, _type):
        self.datetime = _datetime
        self.raw_time = raw_time
        self.type = _type


class ArgToDuration(commands.Converter):
    """Converter that returns a `Duration` object."""

    async def convert(self, ctx: commands.Context, argument: str = None):

        if not argument:
            return None  # Not sure that if I remove this condition the converter would return None
        try:
            if argument.endswith(("s", "sec", "second", "seconds")):
                raw_time, duration_type = int(remove_chars(
                    argument, "seconds ", "")), "second(s)"
                _datetime = datetime.datetime.utcnow() + datetime.timedelta(seconds=raw_time)
            elif argument.endswith(("m", "min", "minute ", "minutes")):
                raw_time, duration_type = int(remove_chars(
                    argument, "minutes ", "")), "minute(s)"
                _datetime = datetime.datetime.utcnow() + datetime.timedelta(minutes=raw_time)
            elif argument.endswith(("h", "hour", "hours")):
                raw_time, duration_type = int(
                    remove_chars(argument, "hours ", "")), "hour(s)"
                _datetime = datetime.datetime.utcnow() + datetime.timedelta(hours=raw_time)
            elif argument.endswith(("d", "day", "days")):
                raw_time, duration_type = int(
                    remove_chars(argument, "days ", "")), "day(s)"
                _datetime = datetime.datetime.utcnow() + datetime.timedelta(days=raw_time)
            elif argument.endswith(("w", "week", "weeks")):
                raw_time, duration_type = int(
                    remove_chars(argument, "weeks ", "")), "week(s)"
                _datetime = datetime.datetime.utcnow() + datetime.timedelta(weeks=raw_time)
            elif argument.endswith(("month", "months")):
                raw_time, duration_type = int(remove_chars(
                    argument, "months ", "")), "month(s)"
                _datetime = datetime.datetime.utcnow() + datetime.timedelta(seconds=raw_time *
                                                                            2629800)  # Doesn't support "month" parameter
            # Who bans for a year ? Seriously
            elif argument.endswith(("y", "year", "years")):
                raw_time, duration_type = int(
                    remove_chars(argument, "years ", "")), "year(s)"
                _datetime = datetime.datetime.utcnow() + datetime.timedelta(seconds=raw_time*31557600)
            # This was tricky, I'm sure there's a better way to do this. If it's the case don't hesitate to tell me 😏
            return Duration(_datetime, raw_time, duration_type)
        except (ValueError, NameError):
            raise commands.BadArgument


def plugin_is_enabled():
    async def predicate(ctx):
        if ctx.guild:
            client.cursor.execute(
                f"SELECT enabled FROM mod_plugin WHERE guild_id=?",
                (ctx.guild.id,)
            )
            enabled = client.cursor.fetchone()
            if enabled:
                enabled = enabled[0]
            return enabled
        else:
            return True
    return commands.check(predicate)


class Mod(commands.Cog):
    def __init__(self, client):
        self.client: Shibbot = client
        self.sanctions_init = False

        self.client.cursor.execute(
            "CREATE TABLE IF NOT EXISTS sanctions(guild_id INTEGER, user_id INTEGER, type TEXT, duration DATETIME)")
        self.client.cursor.execute(
            "CREATE TABLE IF NOT EXISTS warns(guild_id INTEGER, user_id INTEGER, reason TEXT, date DATETIME)")
        self.client.cursor.execute(
            "CREATE TABLE IF NOT EXISTS mod_plugin(guild_id INTEGER PRIMARY KEY, enabled BOOLEAN, mute_role INTEGER, logs_channel INTEGER)")
        self.client.db.commit()

        self.resume_sanctions.start()

    async def log(self, guild: discord.Guild, embed):
        self.client.cursor.execute(
            f"SELECT logs_channel FROM mod_plugin WHERE guild_id=?",
            (guild.id,))
        logs_channel_id = self.client.cursor.fetchone()
        if not logs_channel_id:
            return
        logs_channel = guild.get_channel(logs_channel_id[0])
        if not logs_channel:
            return
        return await logs_channel.send(embed=embed)

    @commands.Cog.listener()
    @plugin_is_enabled()
    async def on_member_remove(self, member: discord.Member):
        await asyncio.sleep(0.5)
        found_entry = None
        async for entry in member.guild.audit_logs(
            action=discord.AuditLogAction.kick,
            limit=50
        ):
            if entry.target.id == member.id:
                found_entry = entry
                break
        if found_entry:
            embed_text = self.client.fl(self.client.get_lang(
                member)).log_on_member_remove["embed"]
            await self.log(
                member.guild,
                embed=LogEmbed(
                    embed_text["action"],
                    embed_text["description"].format(
                        member=member.mention,
                        member_id=member.id,
                        mod=found_entry.user.mention.id,
                        reason=found_entry.reason
                    ),
                    found_entry.created_at
                )
            )

    @ commands.Cog.listener()
    @ plugin_is_enabled()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        await asyncio.sleep(0.5)
        found_entry = None
        async for entry in guild.audit_logs(
            action=discord.AuditLogAction.ban,
            limit=50
        ):
            if entry.target.id == user.id:
                found_entry = entry
                break
        if found_entry:
            embed_text = self.client.fl(self.client.get_lang(
                guild)).log_on_member_remove["embed"]
            await self.log(
                guild,
                embed=LogEmbed(
                    embed_text["action"],
                    embed_text["description"].format(
                        user=user.mention,
                        user_id=user.id,
                        mod=found_entry.user.mention.id,
                        reason=found_entry.reason
                    ),
                    found_entry.created_at
                )
            )

    @commands.Cog.listener()
    @plugin_is_enabled()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        await asyncio.sleep(0.5)
        found_entry = None
        async for entry in guild.audit_logs(
            action=discord.AuditLogAction.unban,
            limit=50
        ):
            if entry.target.id == user.id:
                found_entry = entry
                break
        if found_entry:
            embed_text = self.client.fl(self.client.get_lang(
                guild)).log_on_member_remove["embed"]
            await self.log(
                guild,
                embed=LogEmbed(
                    embed_text["action"],
                    embed_text["description"].format(
                        user=user.mention,
                        user_id=user.id
                    ),
                    found_entry.created_at
                )
            )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        self.client.cursor.execute(
            f"DELETE FROM sanctions WHERE guild_id=?",
            (guild.id,)
        )
        self.client.db.commit()

    @tasks.loop(count=1)
    async def resume_sanctions(self):
        """Resume the temp commands (tban, tmute) if the bot went offline."""
        if not self.sanctions_init:
            self.sanctions_init = True
            self.client.cursor.execute("SELECT * FROM sanctions")
            all_sanctions = self.client.cursor.fetchall()
            tasks = [
                self.add_temp_sanction(
                    *sanction[0:len(sanction)-1],
                    duration=datetime.datetime.strptime(
                        sanction[3], "%Y-%m-%d %H:%M:%S.%f"
                    )
                ) for sanction in all_sanctions
            ]
            print(
                f"[+] Resuming tempmute and tempban sanctions ({len(tasks)} ones).")
            await asyncio.gather(*tasks)

    async def add_temp_sanction(self, guild_id: int, user_id: int, type: str, duration: datetime.datetime):
        seconds = (duration - datetime.datetime.utcnow()).total_seconds()
        if seconds < 1:  # Can't be negative so set to 1 second.
            seconds = 1
        await asyncio.sleep(seconds)
        while not self.client.bot_is_alive:
            # Verifies each seconds if the bot is connected.
            await asyncio.sleep(1.0)

        guild: discord.Guild = self.client.get_guild(guild_id)
        if not guild:
            self.client.cursor.execute(
                f"DELETE FROM sanctions WHERE guild_id=?",
                (guild_id,)
            )
            return self.client.db.commit()

        match type:
            case "tempmute":
                mute_role: discord.Role = await self.get_mute_role(guild)
                member: discord.Member = guild.get_member(user_id)
                if member:
                    try:
                        await member.remove_roles(mute_role)
                    except:
                        pass
                    embed_text = self.client.fl(
                        self.client.get_lang(guild)).log_unmute["embed"]
                    await self.log(
                        member.guild, embed=LogEmbed(
                            embed_text["action"],
                            embed_text["description"].format(
                                member=member.mention,
                                menber_id=member.id
                            )
                        )
                    )
            case "tempban":
                user = await self.client.get_or_fetch_user(user_id)
                if user:
                    try:
                        await guild.unban(user)
                    except:
                        pass

        self.client.cursor.execute(
            f"DELETE FROM sanctions WHERE guild_id=? AND user_id=? AND type=? AND duration=?",
            (guild_id, user_id, type, duration,)
        )  # Would be easier if the sanction had an id :/
        self.client.db.commit()

    async def get_mute_role(self, guild: discord.Guild) -> discord.Role:
        """Gets the mute role of a guild."""
        async def create_mute_role():
            new_role = await guild.create_role(
                name="Muted",
                permissions=discord.Permissions(
                     send_messages=False,
                     speak=False,
                     connect=False,
                     add_reactions=False
                )
            )
            self.client.cursor.execute(
                f"UPDATE mod_plugin SET mute_role=? WHERE guild_id=?",
                (new_role.id, guild.id,)
            )
            self.client.db.commit()
            return new_role

        self.client.cursor.execute(
            f"SELECT mute_role FROM mod_plugin WHERE guild_id=?",
            (guild.id,)
        )
        role_id = self.client.cursor.fetchone()
        if not role_id:  # If a role id was never set in the db
            new_role = await create_mute_role()
            role_id = new_role.id
        role = guild.get_role(role_id)
        if not role:  # If the role doesn't exists anymore
            role = await create_mute_role()
        return role

    @commands.command(name="clear", aliases=["purge"])
    @commands.guild_only()
    @plugin_is_enabled()
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def clear_messages(self, ctx: commands.Context, limit: int = None, member: discord.User = None):
        text = self.client.fl(self.client.get_lang(ctx)).clear
        try:
            limit = int(limit)
            limit = limit if limit <= 100 else 100
        except:
            raise commands.BadArgument
        if not limit:
            embed_text = text["checks"]["missing_args"]["embed"]
            return await ctx.reply(
                embed=discord.Embed(
                    description="( ﾉ ﾟｰﾟ)ﾉ "+embed_text["description"],
                    color=discord.Color.red()
                )
            )

        async with ctx.typing():
            if member:
                messages = []
                older_than_two_weeks = False
                async for message in ctx.channel.history():
                    # The bot can't bulk delete messages older than 14 days
                    if len(messages) >= limit or message.created_at.timestamp() < (datetime.datetime.utcnow() - datetime.timedelta(days=13.9)).timestamp():
                        older_than_two_weeks = True
                        break
                    if message.author == member:
                        messages.append(message)
                deleted_messages = await ctx.channel.delete_messages(messages)
                embed_text = text["member_clear"]["embed"]
                embed = discord.Embed(
                    description=f"<a:verified:836312937332867072> "+embed_text["description"].format(
                        n_messages=len(messages),
                        member=member.mention
                    ),
                    color=discord.Color.green()
                )
                embed.set_author(
                    name=embed_text["title"],
                    icon_url=member.avatar if member.avatar else None
                )
                if older_than_two_weeks:
                    embed.set_footer(
                        text=embed_text["footer"])
            else:  # No member, classical clear
                await ctx.message.delete()
                deleted_messages = await ctx.channel.purge(limit=limit)
                embed_text = text["channel_clear"]
                embed = discord.Embed(
                    title=embed_text["title"],
                    description=f"<a:verified:836312937332867072> "+embed_text["description"].format(
                        n_messages=len(deleted_messages)
                    ),
                    color=discord.Color.green()
                )
            await ctx.send(
                embed=embed,
                delete_after=10.0
            )


class LogEmbed(discord.Embed):
    def __init__(self, action, _description, _datetime=datetime.datetime.utcnow()):
        super().__init__(title=f"📝 Logs | {action}", description=_description)
        super().set_footer(
            text=f"Shibbot v{__version__} • {_datetime.strftime('%d %b %Y')}")
