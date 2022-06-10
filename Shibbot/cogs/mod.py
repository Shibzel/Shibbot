import datetime
import asyncio
import datetime

import discord
from discord.ext import commands

from bot import Shibbot, __version__
from utils import remove_chars, ArgToDuration


client = None


def setup(_client):
    global client
    client = _client
    client.add_cog(Mod(client))


def plugin_is_enabled():
    async def predicate(ctx):
        if ctx.guild:
            async with client.aiodb() as db:
                async with db.execute(
                    f"SELECT enabled FROM mod_plugin WHERE guild_id=?",
                    (ctx.guild.id,)
                ) as cursor:
                    enabled = await cursor.fetchone()
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
            "CREATE TABLE IF NOT EXISTS warns(guild_id INTEGER, user_id INTEGER, reason TEXT, date DATETIME, mod_id INTEGER)")
        self.client.cursor.execute(
            "CREATE TABLE IF NOT EXISTS mod_plugin(guild_id INTEGER PRIMARY KEY, enabled BOOLEAN, mute_role INTEGER, logs_channel INTEGER)")
        self.client.db.commit()

        self.client.loop.create_task(self.resume_sanctions())

    async def log(self, guild: discord.Guild, embed):
        async with self.client.aiodb() as db:
            async with db.execute(
                "SELECT logs_channel FROM mod_plugin WHERE guild_id=?",
                (guild.id,)
            ):
                logs_channel_id = self.client.cursor.fetchone()
        if not logs_channel_id:
            return
        logs_channel = guild.get_channel(logs_channel_id[0])
        if not logs_channel:
            return
        return await logs_channel.send(embed=embed)

    async def add_temp_sanction(self, guild_id: int, user_id: int, type: str, duration: datetime.datetime):
        seconds = (duration - datetime.datetime.utcnow()).total_seconds()
        if seconds < 1:  # Can't be negative so set to 1 second.
            seconds = 1
        await asyncio.sleep(seconds)
        while not self.client.bot_is_alive:
            # Verifies each seconds if the bot is connected.
            await asyncio.sleep(1.0)

        guild: discord.Guild = self.client.get_guild(guild_id)
        async with self.client.aiodb() as db:
            if not guild:
                async with db.execute(
                    f"DELETE FROM sanctions WHERE guild_id=?",
                    (guild_id,)
                ):
                    return await db.commit()

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
                                    member_id=member.id
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

            async with db.execute(
                f"DELETE FROM sanctions WHERE guild_id=? AND user_id=? AND type=? AND duration=?",
                (guild_id, user_id, type, duration,)
            ):  # Would be easier if the sanction had an id :/
                await db.commit()

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

    @commands.command(name="logs", aliases=["setlogs"])
    @commands.guild_only()
    @plugin_is_enabled()
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(3, 30, commands.BucketType.member)
    async def change_logs_channel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        text = self.client.fl(await self.client.get_lang(ctx)).change_logs_channel
        if not channel:
            embed_text = text["checks"]["missing_args"]["embed"]
            return await ctx.reply(
                embed=discord.Embed(
                    description="( ﾉ ﾟｰﾟ)ﾉ "+embed_text["description"],
                    color=discord.Color.dark_gold()
                )
            )

        self.client.cursor.execute(
            "UPDATE mod_plugin SET logs_channel=? WHERE guild_id=?",
            (channel.id, ctx.guild.id,)
        )
        self.client.db.commit()
        embed_text = text["embed"]
        await ctx.reply(
            embed=discord.Embed(
                title=embed_text["title"],
                description=f"<a:verified:836312937332867072> " +
                embed_text["description"].format(channel=channel.mention),
                color=discord.Color.green()
            )
        )

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
                        mod=found_entry.user.mention,
                        reason=found_entry.reason
                    ),
                    found_entry.created_at
                )
            )

    @commands.Cog.listener()
    @plugin_is_enabled()
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
                        member=user.mention,
                        member_id=user.id,
                        mod=found_entry.user.mention,
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
                        member=user.mention,
                        member_id=user.id
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

    @commands.command(name="clear", aliases=["purge"])
    @commands.guild_only()
    @plugin_is_enabled()
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def clear_messages(self, ctx: commands.Context, limit: int = None, member: discord.User = None):
        text = self.client.fl(await self.client.get_lang(ctx)).clear_messages
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
                embed_text = text["channel_clear"]["embed"]
                embed = discord.Embed(
                    title=embed_text["title"],
                    description=f"<a:verified:836312937332867072> "+embed_text["description"].format(
                        n_messages=len(deleted_messages)
                    ),
                    color=discord.Color.green()
                )
            return await ctx.send(
                embed=embed,
                delete_after=10.0
            )

    @commands.command(name="nuke")
    @commands.guild_only()
    @plugin_is_enabled()
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 15, commands.BucketType.member)
    async def nuke_channel(self, ctx: commands.Context):
        text = self.client.fl(await self.client.get_lang(ctx)).nuke_channel
        embed_text = text["embed"]
        embed = discord.Embed(
            title=embed_text["title"],
            description=embed_text["description"],
            color=discord.Color.red()
        )
        buttons_text = text["buttons"]
        no_button = discord.ui.Button(
            label=buttons_text["no"],
            style=discord.ButtonStyle.green
        )
        kadaboom_button = discord.ui.Button(
            label=buttons_text["yes"],
            style=discord.ButtonStyle.danger
        )

        async def go_back_callback(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return
            no_button.disabled = True
            kadaboom_button.disabled = True
            await interaction.response.edit_message(
                view=discord.ui.View(
                    no_button,
                    kadaboom_button
                )
            )
        no_button.callback = go_back_callback

        async def kadaboom_callback(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return
            async with interaction.channel.typing():
                no_button.disabled = True
                kadaboom_button.disabled = True
                await interaction.response.edit_message(
                    view=discord.ui.View(
                        no_button,
                        kadaboom_button
                    )
                )
                await interaction.channel.send(content="3 !")
                await asyncio.sleep(2.0)
                await interaction.channel.send(content="2 !")
                await asyncio.sleep(2.0)
                await interaction.channel.send(content="1 ! <:POG:815700150164652092>")
                await asyncio.sleep(1.0)
                deleted_messages = await interaction.channel.purge(limit=1000)
            embed_text = text["done"]
            embed = discord.Embed(
                title=embed_text["title"],
                description=f"<a:verified:836312937332867072> "+embed_text["description"].format(
                    n_messages=len(deleted_messages)
                ),
                color=discord.Color.red()
            )
            await interaction.channel.send(
                embed=embed,
                delete_after=10
            )
        kadaboom_button.callback = kadaboom_callback

        await ctx.reply(
            embed=embed,
            view=discord.ui.View(
                no_button,
                kadaboom_button
            )
        )

    @commands.command(name="warn")
    @commands.guild_only()
    @plugin_is_enabled()
    @commands.has_permissions(manage_messages=True)
    async def warn_member(self, ctx: commands.Context, member: discord.Member = None, *, reason="Unspecified"):
        text = self.client.fl(await self.client.get_lang(ctx)).warn_member
        if not member:
            embed_text = text["checks"]["missing_args"]["embed"]
            return await ctx.reply(
                embed=discord.Embed(
                    description="( ﾉ ﾟｰﾟ)ﾉ "+embed_text["description"],
                    color=discord.Color.dark_gold()
                )
            )
        if member.id == self.client.user.id:
            return

        self.client.cursor.execute(
            f"SELECT * FROM warns WHERE guild_id=? AND user_id=?",
            (ctx.guild.id, member.id,)
        )
        warns = self.client.cursor.fetchall()
        nb_warns = len(warns)+1 if warns else 1
        self.client.cursor.execute(
            "INSERT INTO warns (guild_id, user_id, reason, date, mod_id) VALUES (?,?,?,?,?)",
            (ctx.guild.id, member.id, reason,
             datetime.datetime.utcnow(), ctx.author.id,)
        )
        self.client.db.commit()
        embed_text = text["embed"]
        embed = discord.Embed(
            description=embed_text["description"].format(
                member=member.mention,
                n_warns=nb_warns,
                reason=reason
            ),
            color=discord.Color.green()
        )
        embed.set_author(
            name=embed_text["title"],
            icon_url=member.avatar if member.avatar else None
        )
        await ctx.message.delete()
        await ctx.send(embed=embed)
        embed_text = text["log"]["embed"]
        await self.log(
            ctx.guild,
            embed=LogEmbed(
                embed_text["action"].format(n_warns=nb_warns),
                embed_text["description"].format(
                    member=member.mention,
                    member_id=member.id,
                    mod=ctx.message.author.mention,
                    reason=reason
                )
            )
        )

        try:
            embed_text = text["pm"]["embed"]
            await member.send(
                embed=discord.Embed(
                    description=embed_text["description"].format(
                        guild=ctx.guild.name,
                        reason=reason
                    ),
                    color=discord.Color.dark_gold()
                )
            )
        except:
            pass

    @commands.command(name="clearwarns", aliases=["cwarns"])
    @commands.guild_only()
    @plugin_is_enabled()
    @commands.has_permissions(manage_messages=True)
    async def clear_user_warns(self, ctx: commands.Context, member: discord.User = None, *, reason="Unspecified"):
        text = self.client.fl(await self.client.get_lang(ctx)).clear_user_warns
        if not member:
            embed_text = text["checks"]["missing_args"]["embed"]
            return await ctx.reply(
                mbed=discord.Embed(
                    description="( ﾉ ﾟｰﾟ)ﾉ "+embed_text["description"],
                    color=discord.Color.dark_gold()
                )
            )
        if member.id == self.client.user.id:
            return

        self.client.cursor.execute(
            f"DELETE FROM warns WHERE guild_id=? AND user_id=?",
            (ctx.guild.id, member.id,)
        )
        self.client.db.commit()
        embed_text = text["embed"]
        embed = discord.Embed(
            description="<a:verified:836312937332867072> "+embed_text["description"].format(
                member=member.mention
            ),
            color=discord.Color.green()
        )
        embed.set_author(
            name=embed_text["title"],
            icon_url=member.avatar if member.avatar else None
        )
        await ctx.message.delete()
        await ctx.send(embed=embed)
        embed_text = text["log"]["embed"]
        await self.log(
            ctx.guild,
            embed=LogEmbed(
                embed_text["action"],
                embed_text["description"].format(
                    mod=ctx.message.author.mention,
                    member=member.mention,
                    reason=reason
                )
            )
        )

    @commands.command(name="warnings", aliases=["infractions"])
    @commands.guild_only()
    @plugin_is_enabled()
    @commands.has_permissions(manage_messages=True)
    async def show_warnings(self, ctx: commands.Context, member: discord.User = None):
        text = self.client.fl(await self.client.get_lang(ctx)).show_warnings
        if not member:
            embed_text = text["checks"]["missing_args"]["embed"]
            return await ctx.reply(
                embed=discord.Embed(
                    description="( ﾉ ﾟｰﾟ)ﾉ "+embed_text["description"],
                    color=discord.Color.dark_gold()
                )
            )
        if member.id == self.client.user.id:
            return

        self.client.cursor.execute(
            "SELECT * FROM warns WHERE guild_id=? AND user_id=?",
            (ctx.guild.id, member.id,)
        )
        warns = self.client.cursor.fetchall()

        embed_text = text["embed"]
        embed = discord.Embed(
            description=embed_text["description"].format(
                member=member.mention,
                member_id=member.id
            ),
            color=discord.Color.dark_gold()
        )
        embed.set_author(
            name=embed_text["title"],
            icon_url=member.avatar if member.avatar else None
        )
        if not warns:
            field_text = embed_text["fields"]["no_infra"]
            embed.add_field(
                name="No infraction",
                value="(⊙ˍ⊙) "+field_text["value"]
            )
            await ctx.message.delete()
            await ctx.send(embed=embed)
        else:
            page = 0
            warns.reverse()

            sorted_warns = []
            page_warns = []
            for warn in warns:
                page_warns.append(warn)
                if len(page_warns) == 5 or warn == warns[-1]:
                    sorted_warns.append(page_warns)
                    page_warns = []

            def generate_warn_page():
                nonlocal page
                embed._fields = []
                page_embed = embed
                field_text = text["embed"]["fields"]["warn"]
                for warn in sorted_warns[page]:
                    mod = self.client.get_user(warn[4])
                    date_time = datetime.datetime.strptime(
                        warn[3], "%Y-%m-%d %H:%M:%S.%f")
                    page_embed.add_field(
                        name=field_text["name"].format(
                            n_warn=warns.index(warn)+1
                        ),
                        value=field_text["value"].format(
                            reason=warn[2],
                            mod=mod.mention if mod else f"<@!{warn[4]}>",
                            date=date_time.strftime("%d %b %Y")
                        ),
                        inline=False
                    )

                return page_embed

            buttons_text = embed_text["buttons"]

            async def previous_page_callback(interaction: discord.Interaction):
                if interaction.user.id != ctx.author.id:
                    return

                nonlocal page
                page -= 1
                if page == 0:
                    previous_page_button.disabled = True
                await interaction.response.edit_message(
                    embed=generate_warn_page(),
                    view=discord.ui.View(
                        previous_page_button,
                        next_page_button
                    )
                )
            previous_page_button = discord.ui.Button(
                style=discord.ButtonStyle.blurple,
                label=buttons_text["previous"],
                disabled=True
            )
            previous_page_button.callback = previous_page_callback

            async def next_page_callback(interaction: discord.Interaction):
                if interaction.user.id != ctx.author.id:
                    return

                nonlocal page
                page += 1
                previous_page_button.disabled = False
                if sorted_warns[page][-1] == warns[-1]:
                    next_page_button.disabled = True
                await interaction.response.edit_message(
                    embed=generate_warn_page(),
                    view=discord.ui.View(
                        previous_page_button,
                        next_page_button
                    )
                )
            next_page_button = discord.ui.Button(
                style=discord.ButtonStyle.green,
                label=buttons_text["next"],
                disabled=True if len(sorted_warns) == 1 else False
            )
            next_page_button.callback = next_page_callback
            await ctx.message.delete()
            await ctx.send(
                embed=generate_warn_page(),
                view=discord.ui.View(
                    previous_page_button,
                    next_page_button,
                )
            )

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
        else:
            role_id = role_id[0]  # If a role was found
        role = guild.get_role(role_id)
        if not role:  # If the role doesn't exists anymore
            role = await create_mute_role()
        return role

    async def set_mute_role(self, ctx: commands.Context, mute_role: discord.Role):
        tasks = [
            channel.set_permissions(
                mute_role,
                overwrite=discord.PermissionOverwrite(
                    send_messages=False,
                    speak=False,
                    connect=False,
                    add_reactions=False
                )
            )
            for channel in ctx.guild.channels
        ]
        await asyncio.gather(*tasks)

    @commands.command(name="mute", aliases=["tg", "shut"])
    @commands.guild_only()
    @plugin_is_enabled()
    @commands.has_permissions(manage_roles=True)
    async def mute_member(self, ctx: commands.Context, member: discord.Member = None, *, reason="Unspecified"):
        text = self.client.fl(await self.client.get_lang(ctx)).mute_member
        if not member:
            embed_text = text["checks"]["missing_args"]["embed"]
            return await ctx.reply(
                embed=discord.Embed(
                    description="( ﾉ ﾟｰﾟ)ﾉ "+embed_text["description"],
                    color=discord.Color.dark_gold()
                )
            )
        if member.id == self.client.user.id:
            return
        await ctx.message.delete()
        mute_role = await self.get_mute_role(ctx.guild)
        if mute_role in member.roles:
            embed_text = text["checks"]["already_muted"]["embed"]
            return await ctx.send(
                embed=discord.Embed(
                    title=embed_text["title"],
                    description="ಠ_ಠ "+embed_text["description"],
                    color=discord.Color.red()
                )
            )

        await self.set_mute_role(ctx, mute_role)
        await member.add_roles(mute_role, reason=reason)
        embed_text = text["embed"]
        embed = discord.Embed(
            description="<a:verified:836312937332867072> "+embed_text["description"].format(
                member=member.mention,
                reason=reason
            ),
            color=discord.Color.green()
        )
        embed.set_author(
            name=embed_text["title"],
            icon_url=member.avatar if member.avatar else None
        )
        await ctx.send(embed=embed)
        embed_text = text["log"]["embed"]
        await self.log(
            ctx.guild,
            embed=LogEmbed(
                embed_text["action"],
                embed_text["description"].format(
                    member=member.mention,
                    member_id=member.id,
                    mod=ctx.author.mention,
                    reason=reason
                )
            )
        )

        try:
            embed_text = text["pm"]["embed"]
            await member.send(
                embed=discord.Embed(
                    description=embed_text["description"].format(
                        guild=ctx.guild.name,
                        reason=reason
                    ),
                    color=discord.Color.dark_gold()
                )
            )
        except:
            pass

    @commands.command(name="tempmute", aliases=["tmute"])
    @commands.guild_only()
    @plugin_is_enabled()
    @commands.has_permissions(manage_roles=True)
    async def tempmute_member(self, ctx: commands.Context, member: discord.Member = None, duration: ArgToDuration = None, *, reason="Unspecified"):
        text = self.client.fl(await self.client.get_lang(ctx)).tempmute_member
        if not member:
            embed_text = text["checks"]["missing_args"]["embed"]
            return await ctx.reply(
                embed=discord.Embed(
                    description="( ﾉ ﾟｰﾟ)ﾉ "+embed_text["description"],
                    color=discord.Color.dark_gold()
                )
            )
        if member.id == self.client.user.id:
            return
        await ctx.message.delete()
        mute_role = await self.get_mute_role(ctx.guild)
        if mute_role in member.roles:
            embed_text = text["checks"]["already_muted"]["embed"]
            return await ctx.send(
                embed=discord.Embed(
                    title=embed_text["title"],
                    description="ಠ_ಠ "+embed_text["description"],
                    color=discord.Color.red()
                )
            )

        await self.set_mute_role(ctx, mute_role)
        await member.add_roles(mute_role, reason=reason)
        data = (ctx.guild.id, member.id, "tempmute", duration.datetime,)
        self.client.cursor.execute(
            "INSERT INTO sanctions (guild_id, user_id, type, duration) VALUES (?,?,?,?)",
            data
        )
        self.client.db.commit()
        embed_text = text["embed"]
        embed = discord.Embed(
            description="<a:verified:836312937332867072> "+embed_text["description"].format(
                member=member.mention,
                duration=duration,
                reason=reason
            ),
            color=discord.Color.green()
        )
        embed.set_author(
            name=embed_text["title"],
            icon_url=member.avatar if member.avatar else None
        )
        await ctx.send(embed=embed)
        embed_text = text["log"]["embed"]
        await self.log(
            ctx.guild,
            embed=LogEmbed(
                embed_text["action"],
                embed_text["description"].format(
                    member=member.mention,
                    member_id=member.id,
                    duration=duration,
                    mod=ctx.author.mention,
                    reason=reason
                )
            )
        )

        try:
            embed_text = text["pm"]["embed"]
            await member.send(
                embed=discord.Embed(
                    description=embed_text["description"].format(
                        guild=ctx.guild.name,
                        duration=duration,
                        reason=reason
                    ),
                    color=discord.Color.dark_gold()
                )
            )
        except:
            pass
        await self.add_temp_sanction(*data)

    @commands.command(name="unmute")
    @commands.guild_only()
    @plugin_is_enabled()
    @commands.has_permissions(manage_roles=True)
    async def unmute_member(self, ctx: commands.Context, member: discord.Member = None):
        lang = self.client.fl(await self.client.get_lang(ctx))
        text = lang.unmute_member
        if not member:
            embed_text = text["checks"]["missing_args"]["embed"]
            return await ctx.reply(
                embed=discord.Embed(
                    description="( ﾉ ﾟｰﾟ)ﾉ "+embed_text["description"],
                    color=discord.Color.dark_gold()
                )
            )
        if member.id == self.client.user.id:
            return
        await ctx.message.delete()
        mute_role = await self.get_mute_role(ctx.guild)
        if not mute_role in member.roles:
            embed_text = text["checks"]["not_muted"]["embed"]
            return await ctx.send(
                embed=discord.Embed(
                    title=embed_text["title"],
                    description="ಠ_ಠ "+embed_text["description"],
                    color=discord.Color.red()
                )
            )

        await member.remove_roles(mute_role)
        embed_text = text["embed"]
        embed = discord.Embed(
            description=embed_text["description"].format(
                member=member.mention),
            color=discord.Color.green()
        )
        embed.set_author(
            name=embed_text["title"],
            icon_url=member.avatar if member.avatar else None
        )
        await ctx.send(embed=embed)
        embed_text = text["log"]["embed"]
        embed_text = lang.log_unmute["embed"]
        await self.log(
            member.guild, embed=LogEmbed(
                embed_text["action"],
                embed_text["description"].format(
                    member=member.mention,
                    member_id=member.id
                )
            )
        )

        try:
            embed_text = text["pm"]["embed"]
            await member.send(
                embed=discord.Embed(
                    description=embed_text["description"].format(
                        guild=ctx.guild.name
                    ),
                    color=discord.Color.dark_gold()
                )
            )
        except:
            pass


class LogEmbed(discord.Embed):
    def __init__(self, action, _description, _datetime=datetime.datetime.utcnow()):
        super().__init__(title=f"📝 Logs | {action}", description=_description)
        super().set_footer(
            text=f"Shibbot v{__version__} • {_datetime.strftime('%d %b %Y')}")
