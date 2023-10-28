import time
import asyncio
from datetime import datetime, timedelta
import discord
from discord.ext import bridge, commands

from src.core import Shibbot
from src.models import PluginCog

from .lang import English
from .converters import secs_to_humain


PLUGIN_NAME = "mod"

class SanctionType:
    warn = "warn"
    ban = "ban"
    tempban = "tempban"
    softban = "softban"
    kick = yeet = "kick"
    mute = stfu = "mute"
    tempmute = "tempmute"

class LogEmbed(discord.Embed):
    def __init__(self, title: str, user: discord.User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        title = f"📜 Log | {title}"
        if user and user.avatar:
            self.set_author(name=title, icon_url=user.avatar)
        else:
            self.title = title
        self.timestamp = datetime.utcnow()

class Moderation(PluginCog):
    def __init__(self, bot: Shibbot):
        self.bot = bot
        super().__init__(
            plugin_name=PLUGIN_NAME,
            guild_only=True,
            name={
                "en": "Moderation",
                "fr": "Modération"
            },
            description={
                "en": "Tools to moderate your server.",
                "fr": "Des outils pour modérer votre serveur."
            },
            languages={
                "en": English(),
                # "fr": French(),
            },
            emoji="👮"
        )
        self.mute_kwargs = {"send_messages": False, "add_reactions": False}
        
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.plugin_name} (
            guild_id    INTEGER PRIMARY KEY,
            log         BOOLEAN DEFAULT 1,
            log_channel INTEGER,
            mute_role   INTEGER
        );
        CREATE TABLE IF NOT EXISTS {self.plugin_name}_sanctions (
            guild_id    INTEGER NOT NULL,
            user_id     INTEGER NOT NULL,
            type        TEXT NOT NULL,
            timestamp   REAL NOT NULL
        );
        CREATE INDEX IF NOT EXISTS {self.plugin_name}_idx_guild_sanctions
            ON {self.plugin_name}_sanctions (guild_id, user_id, type, timestamp);
        CREATE TABLE IF NOT EXISTS {self.plugin_name}_warns (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id    INTEGER NOT NULL,
            member_id   INTEGER NOT NULL,
            mod_id      INTEGER NOT NULL,
            time        REAL NOT NULL,
            reason      TEXT
        );
        CREATE INDEX IF NOT EXISTS {self.plugin_name}_idx_guild_warns
            ON {self.plugin_name}_warns (guild_id, member_id)
        """
        self.bot.db.executescript(query) # VER: v1.0.0
        self.bot.db.commit()
    
    async def shedule_sanction(
        self,
        guild_id: int,
        user_id: int,
        sanction_type: str,
        timestamp: float
    ) -> None:
        dur = timestamp - time.time()
        await asyncio.sleep(dur if dur > 0 else 1)
            
        if not (guild := self.bot.get_guild(guild_id)):
            return
        
        db = self.bot.db
        query = f"""SELECT id FROM {self.plugin_name}_sancrions 
                    WHERE guild_id=? AND user_id=? AND type=? AND timestamp=?"""
        args = (guild_id, user_id, sanction_type, timestamp,)
        cur = db.execute(query, args)
        if not (result := cur.fetchone()):
            return  # The sanction doesn't exist anymore
        sanction_id = result[0]
        
        try:
            if sanction_type == SanctionType.tempmute:
                if member := guild.get_member(user_id):
                    mute_role = await self.get_mute_role(guild)
                    if mute_role in member.roles:
                        reason = "End of tempmute."
                        await member.remove_roles(mute_role, reason=reason)
                await self.on_unmute(member, self.bot.user, reason, remove_from_db=False)
            elif sanction_type == SanctionType.tempban:
                async for ban_entry in guild.bans():
                    if user_id == (user := ban_entry.user).id:
                        reason = "End of tempban."
                        await guild.unban(user, reason=reason)
                        await self.on_unban(user, self.bot.user, reason)
                        break
        except discord.Forbidden as err:
            self.logger.debug(f"Couldn't un-{sanction_type} on '{guild.name}' (ID: {guild.id})"
                              f"because of a permission error. Sanction ID: {sanction_id}.", err)
        except Exception as err:
            self.logger.error(
                f"An unexpected error occured while trying to un-{sanction_type}."
                f" Sanction ID: {sanction_id}.", err)
            return
        
        query = f"DELETE FROM {self.plugin_name}_sancrions WHERE id=?"
        db.execute(query, (sanction_id,))
        db.commit()
    
    async def when_ready(self) -> None:
        self.logger.debug("Fetching sheduled sanctions.")
        db = self.bot.db
        query = f"""SELECT guild_id, user_id, type, timestamp FROM {self.plugin_name}_sanctions
                    WHERE type IN (?, ?)"""
        cur = db.execute(query, (SanctionType.tempmute, SanctionType.tempban))
        if not (temporary_sanctions := cur.fetchall()):
            return
            
        bot_guilds = {guild.id for guild in self.bot.guilds}
        sanctions_guilds = {sanction[0] for sanction in temporary_sanctions}
        suitable_guilds = bot_guilds & sanctions_guilds
        
        if guilds_to_remove := sanctions_guilds - suitable_guilds:
            query = f"""DELETE FROM {self.plugin_name}_sanctions
                        WHERE guild_id IN ({','.join('?'*len(guilds_to_remove))})"""
            db.execute(query, guilds_to_remove)
            
        tasks = [
            self.shedule_sanction(*sanction)
            for sanction in temporary_sanctions
            if sanction[0] in suitable_guilds
        ]
        if tasks:
            self.logger.debug(f"Resuming {len(tasks)} tempbans and tempmutes.")
            await asyncio.gather(*tasks)
        else:
            self.logger.debug("Nothing to do.")
            
    async def enable_logs(self, guild_id,):
        pass  # TODO: Complete
    
    def get_log_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        db = self.bot.db
        query = f"SELECT log, log_channel FROM {self.plugin_name} WHERE guild_id=?"
        cur = db.execute(query, (guild.id,))
        if not (result := cur.fetchone()):
            return  # Guild not in database
        log, log_channel_id = result
        if not log or not log_channel_id:
            return  # Logs are disabled or channel is not set
        return guild.get_channel(log_channel_id) # Can either be None or discord.TextChannel
    
    async def setup_mute_role(self, mute_role: discord.Role) -> None:
        guild = mute_role.guild
        overwrite = discord.PermissionOverwrite(**self.mute_kwargs)
        tasks = [
            channel.set_permissions(mute_role, overwrite=overwrite)
            for channel in guild.text_channels
            if mute_role not in channel.overwrites
        ]
        if tasks:
            await asyncio.gather(*tasks)
    
    async def get_mute_role(self, guild: discord.Guild) -> discord.Role:
        db = self.bot.db
        query = f"SELECT mute_role FROM {self.plugin_name} WHERE guild_id=?"
        cur = db.execute(query, (guild.id,))
        result = cur.fetchone()
        if result and (mute_role := guild.get_role(result[0])):
            self.bot.loop.create_task(self.setup_mute_role(mute_role))
            return mute_role
        permissions = discord.Permissions(**self.mute_kwargs)
        mute_role = await guild.create_role(name="Mute", permissions=permissions,
                                            color=discord.Color.dark_red())

        query = f"INSERT INTO {self.plugin_name} (guild_id, mute_role) VALUES (?, ?)"
        db.execute(query, (guild.id, mute_role.id,))
        db.commit()
        self.bot.loop.create_task(self.setup_mute_role(mute_role))
        return mute_role
            
    async def get_warns(self, guild: discord.Guild, user: discord.User) -> tuple[int, int, int, float, str | None]:
        db = self.bot.db
        query = f"SELECT * FROM {self.plugin_name}_warns WHERE guild_id=? AND member_id=?"
        cur = db.execute(query, (guild.id, user.id,))
        return cur.fetchall()
    
    async def _find_entry(
        self,
        guild: discord.Guild,
        user: discord.User,
        action: discord.AuditLogAction
    ) -> discord.AuditLogEntry | None:
        async for entry in guild.audit_logs(action=action, limit=50):
            if entry.target == user:
                return entry if user != self.bot.user else None
    
    async def on_kick(
        self,
        member: discord.Member,
        moderator: discord.Member,
        reason: str = None,
        lang: English = None,
        log_channel: discord.TextChannel = None,
    ) -> None:
        guild = member.guild
        if not (log_channel := log_channel or self.get_log_channel(guild)):
            return
        if not lang:
            lang = self.get_lang(guild)
        
        description = lang.ON_KICK_DESCRIPTION.format(
            member=member, mod=moderator, reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_KICK_TITLE, user=member,
                         description=description, color=discord.Color.red())
        await log_channel.send(embed=embed)
    
    @discord.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild
        if not (log_channel := self.get_log_channel(guild)):
            return
        await asyncio.sleep(0.5)
        if found_entry := await self._find_entry(guild, member, discord.AuditLogAction.kick):
            await self.on_kick(member, found_entry.user, found_entry.reason, log_channel=log_channel)

    async def on_ban(
        self,
        user: discord.User,
        moderator: discord.Member,
        reason: str = None,
        lang: English = None,
        log_channel: discord.TextChannel = None,
    ) -> None:
        guild = moderator.guild            
        if not (log_channel := log_channel or self.get_log_channel(guild)):
            return
        if not lang:
            lang = self.get_lang(guild)
        
        description = lang.ON_BAN_DESCRIPTION.format(
            user=user, mod=moderator, reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_BAN_TITLE, user=user,
                         description=description, color=discord.Color.dark_red())
        await log_channel.send(embed=embed)
        
    async def on_temp_ban(
        self,
        user: discord.User,
        moderator: discord.Member,
        timestamp: float,
        reason: str = None,
        lang: English = None,
        log_channel: discord.TextChannel = None,
    ) -> None:
        guild = moderator.guild
        db = self.bot.db
        query = f"""INSERT INTO {self.plugin_name}_sanctions (guild_id, user_id, mod_id, timestamp, reason)
                    VALUES (?, ?, ?, ?, ?)"""

        db.execute(query, (guild.id, user.id, moderator.id, timestamp, reason))
        await self.shedule_sanction(guild.id, user.id, SanctionType.tempban, timestamp)
                 
        if not (log_channel := log_channel or self.get_log_channel(guild)):
            return
        if not lang:
            lang = self.get_lang(guild)
        
        duration = secs_to_humain(time.time() - timestamp)
        description = lang.ON_TEMPBAN_DESCRIPTION.format(
            user=user, mod=moderator, duration=duration,
            reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_TEMPBAN_TITLE, user=user,
                         description=description, color=discord.Color.greyple())
        await log_channel.send(embed=embed)

    @discord.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        if not (log_channel := self.get_log_channel(guild)):
            return
        await asyncio.sleep(0.5)
        if found_entry := await self._find_entry(guild, user, discord.AuditLogAction.ban):
            await self.on_ban(user, found_entry.user, found_entry.reason, log_channel=log_channel)
            
    async def on_unban(
        self,
        user: discord.User,
        moderator: discord.Member,
        reason: str = None,
        lang: English = None,
        log_channel: discord.TextChannel = None,
    ) -> None:
        guild = moderator.guild
        if not (log_channel := log_channel or self.get_log_channel(guild)):
            return
        if not lang:
            lang = self.get_lang(guild)
        
        description = lang.ON_UNBAN_DESCRIPTION.format(
            user=user, mod=moderator, reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_UNBAN_TITLE, user=user,
                         description=description, color=discord.Color.greyple())
        await log_channel.send(embed=embed)

    @discord.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        if not (log_channel := self.get_log_channel(guild)):
            return
        await asyncio.sleep(0.5)
        if found_entry := await self._find_entry(guild, user, discord.AuditLogAction.unban):
            await self.on_unban(user, found_entry.user, found_entry.reason, log_channel=log_channel)
            
    async def on_warn(
        self,
        member: discord.Member,
        moderator: discord.Member,
        warns: int = None,
        reason: str = None,
        lang: English = None,
        log_channel: discord.TextChannel = None,
    ) -> None:
        guild = member.guild
        db = self.bot.db
        query = f"""INSERT INTO {self.plugin_name}_warns (guild_id, member_id, mod_id, time, reason)
                    VALUES (?, ?, ?, ?, ?)"""

        db.execute(query, (guild.id, member.id, moderator.id, reason))
            
        if not (log_channel := log_channel or self.get_log_channel(guild)):
            return
        if not lang:
            lang = self.get_lang(guild)
        if not warns:
            warns = len(await self.get_warns(guild, member))
        
        description = lang.ON_WARN_DESCRIPTION.format(user=member, mod=moderator, reason=reason)
        embed = LogEmbed(title=lang.ON_WARN_TITLE.format(warns=warns), user=member,
                         description=description, color=discord.Color.orange())
        await log_channel.send(embed=embed)
        
    async def on_mute(
        self,
        member: discord.Member,
        moderator: discord.Member,
        reason: str = None,
        update_from_db: bool = True,
        lang: English = None,
        log_channel: discord.TextChannel = None
    ) -> None:
        guild = member.guild
        if update_from_db:
            db = self.bot.db
            query = f"""INSERT INTO {self.plugin_name}_sanctions (guild_id, user_id, type)
                        VALUES (?, ?, ?, ?)"""
    
            db.execute(query, (guild.id, member.id, SanctionType.mute,))
    
        if not (log_channel := log_channel or self.get_log_channel(member.guild)):
            return
        if not lang:
            lang = self.get_lang(guild)
            
        description = lang.ON_MUTE_DESCRIPTION.format(
            member=member, mod=moderator, reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_MUTE_TITLE, member=member,
                         description=description, color=discord.Color.yellow())
        await log_channel.send(embed=embed)
        
    async def on_temp_mute(
        self,
        member: discord.Member,
        moderator: discord.Member,
        timestamp: float,
        reason: str = None,
        lang: English = None,
        log_channel: discord.TextChannel = None,
    ) -> None:
        guild = member.guild
        db = self.bot.db
        query = f"""INSERT INTO {self.plugin_name}_sanctions (guild_id, user_id, mod_id, timestamp, reason)
                    VALUES (?, ?, ?, ?, ?)"""

        db.execute(query, (guild.id, member.id, moderator.id, timestamp, reason))
        await self.shedule_sanction(guild.id, member.id, SanctionType.tempmute, timestamp)
                 
        if not (log_channel := log_channel or self.get_log_channel(guild)):
            return
        if not lang:
            lang = self.get_lang(guild)
        
        duration = secs_to_humain(time.time()-timestamp)
        description = lang.ON_TEMPMUTE_DESCRIPTION.format(
            member=member, mod=moderator, duration=duration,
            reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_TEMPMUTE_TITLE, member=member,
                         description=description, color=discord.Color.yellow())
        await log_channel.send(embed=embed)
        
    async def on_unmute(
        self,
        member: discord.Member,
        moderator: discord.Member,
        reason: str = None,
        remove_from_db: bool = True,
        lang: English = None,
        log_channel: discord.TextChannel = None
    ) -> None:
        guild = member.guild
        if remove_from_db:
            db = self.bot.db
            query = f"""DELETE FROM {self.plugin_name}_sanctions
                        WHERE guild_id=? AND user_id=? AND type=?"""
            db.execute(query, (guild.id, member.id, SanctionType.mute))
        
        if not (log_channel := log_channel or self.get_log_channel(guild)):
            return
        if not lang:
            lang = self.get_lang(guild)
        
        description = lang.ON_UNMUTE_DESCRIPTION.format(
            member=member, mod=moderator, reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_UNMUTE_TITLE, member=member,
                         description=description, color=discord.Color.greyple())
        await log_channel.send(embed=embed)
        
    @discord.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        db = self.bot.db
        query = f"""SELECT id FROM {self.plugin_name}_sanctions
                    WHERE guild_id=? AND user_id=? AND type IN (?, ?)"""
        cur = db.execute(query, (guild.id, member.id, SanctionType.mute, SanctionType.tempmute))
        if not cur.fetchone():
            return
        
        mute_role = await self.get_mute_role(guild)
        await member.add_roles(mute_role)
        await self.on_mute(member, self.bot.user, "User joined while he was muted.", update_from_db=False)
    
    async def set_log_channel(self, channel: discord.TextChannel, lang: English = None) -> None:
        guild = channel.guild
        db = self.bot.db
        query = f"SELECT log_channel FROM {self.plugin_name} WHERE guild_id=?"
        cur = db.execute(query, (guild.id,))
        result = cur.fetchone()
        if result:
            query = f"UPDATE {self.plugin_name} SET log_channel=? WHERE guild_id=?"
        else:
            query = f"INSERT INTO {self.plugin_name} (log_channel, guild_id) VALUES (?, ?)"

        db.execute(query, (channel.id, guild.id,))
        db.commit()
        
        if not lang:
            lang = self.get_lang(guild)        
        embed = discord.Embed(title=lang.ON_LOG_CHANNEL_UPDATE_TITLE,
                              description=lang.ON_LOG_CHANNEL_UPDATE_DESCRIPTION,
                              color=discord.Color.green())
        log_channel = self.get_log_channel(guild)
        await log_channel.send(embed=embed)

    @bridge.bridge_command(
        name="logs",
        description="Changes the log channel.",
        options=[discord.Option(discord.TextChannel, name="channel", description="The log channel.")]
    )
    @bridge.has_permissions(manage_channels=True)
    @commands.cooldown(2, 15, commands.BucketType.guild)
    async def _set_log_channel(self, ctx: bridge.BridgeApplicationContext, channel: discord.TextChannel) -> None:
        lang: English = self.get_lang(ctx)
        
        await self.set_log_channel(channel, lang)
        
        description = lang.SET_LOG_CHANNEL_DESCRIPTION.format(channel=channel)
        embed = discord.Embed(title=lang.SET_LOG_CHANNEL_TITLE, description=description,
                              color=discord.Color.green())
        await ctx.respond(embed=embed)
        
    async def on_purge(
        self,
        channel: discord.TextChannel | discord.Thread,
        messages: int,
        moderator: discord.Member,
        user: discord.User = None,
        reason: str = None,
        lang: English = None,
        log_channel: discord.TextChannel = None
    ) -> None:
        guild = channel.guild
        if not (log_channel := log_channel or self.get_log_channel(guild)):
            return
        if not lang:
            lang = self.get_lang(guild)
            
        description = lang.ON_PURGE_USER_DESCRIPTION if user else lang.ON_PURGE_CHANNEL_DESCRIPTION
        description = description.format(user=user, mod=moderator, messages=messages, channel=channel,
                                         reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_PURGE_TITLE, user=user,
                         description=description, color=discord.Color.yellow())
        await log_channel.send(embed=embed)
    
    @bridge.bridge_command(
        name="clear",
        aliases=["purge"],
        options=[
            discord.Option(int, name="limit", description="The number of messages you want to clear, maximum: 100."),
            discord.Option(str, name="reason", description="Why.", required=False)
    ])
    async def clear_channel(self, ctx: bridge.BridgeApplicationContext, limit: int, reason: str = None):
        lang: English = self.get_lang(ctx)

        limit += 1
        if limit > 100:
            limit = 100

        await ctx.defer()
        deleted_messages = len(await ctx.channel.purge(limit=limit) or ())
        description = lang.CLEAN_MESSAGES_DESCRIPTION.format(
            messages=deleted_messages)
        
        embed = discord.Embed(title=lang.CLEAN_MESSAGES_TITLE, description=description,
                              color=discord.Color.green())
        await ctx.send(embed=embed)
        await self.on_purge(ctx.channel, deleted_messages, ctx.author, reason=reason, lang=lang)

    @bridge.bridge_command(
        name="clearuser",
        aliases=["purgeuser"],
        options=[
            discord.Option(int, name="limit", description="The number of messages you want to clear, maximum: 1000."),
            discord.Option(discord.User, name="user", description="The user you want to clean the messages from."),
            discord.Option(str, name="reason", description="Why.", required=False)
    ])
    async def clean_user_messages(self, ctx: bridge.BridgeApplicationContext, limit: int, user: discord.User, reason: str = None):
        lang: English = self.get_lang(ctx)

        if limit > 1000:
            limit = 1000

        async with ctx.channel.typing():
            messages = []
            after = datetime.utcnow() - timedelta(days=14-0.5)
            async for message in ctx.channel.history(limit=None, after=after):
                # The bot can't bulk delete messages older than 14 days
                if len(messages) >= limit:
                    break
                if message.author == user:
                    messages.append(message)
            deleted_messages = len(await ctx.channel.delete_messages(messages) or ())
            description = lang.CLEAN_MESSAGES_USER_DESCRIPTION.format(
                messages=deleted_messages,
                user=user)
        
        embed = discord.Embed(title=lang.CLEAN_MESSAGES_TITLE, description=description,
                              color=discord.Color.green())
        await ctx.respond(embed=embed)
        await self.on_purge(ctx.channel, deleted_messages, ctx.author, user, reason, lang)


def setup(bot):
    bot.add_cog(Moderation(bot))