import time
import asyncio
from datetime import datetime
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
        title = f"📜 Log | {title}"
        if user and user.avatar:
            self.set_author(name=title, icon_url=user.avatar)
        else:
            self.title = title
        self.timestamp = datetime.utcnow()
        super().__init__(*args, **kwargs)

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
                "en": English,
                # "fr": French,
            },
            emoji="👮"
        )
        self.mute_kwargs = {"send_messages": False, "add_reactions": False}
        
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.plugin_name} (
            guild_id    INTEGER PRIMARY KEY,
            log         BOOLEAN NOT NULL,
            log_channel INTEGER,
            mute_role   INTEGER
        );
        CREATE TABLE IF NOT EXISTS {self.plugin_name}_sanctions (
            guild_id    INTEGER NOT NULL,
            user_id     INTEGER NOT NULL,
            type        TEXT NOT NULL,
            timestamp    REAL NOT NULL
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
        
        db = self.bot.asyncdb
        query = f"""SELECT id FROM {self.plugin_name}_sancrions 
                    WHERE guild_id=? AND user_id=? AND type=? AND timestamp=?"""
        args = (guild_id, user_id, sanction_type, timestamp,)
        async with db.execute(query, args) as cursor:
            if not (result := await cursor.fetchone()):
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
        
        async with db:
            query = f"DELETE FROM {self.plugin_name}_sancrions WHERE id=?"
            await db.execute(query, (sanction_id,))
    
    async def when_ready(self) -> None:
        db = self.bot.asyncdb
        query = f"""SELECT guild_id, user_id, type, timestamp FROM {self.plugin_name}_sanctions
                    WHERE type IN (?, ?)"""
        async with db.execute(query, (SanctionType.tempmute, SanctionType.tempban)) as cursor:
            if not (temporary_sanctions := await cursor.fetchall()):
                return
            
        bot_guilds = {guild.id for guild in self.bot.guilds}
        sanctions_guilds = {sanction[0] for sanction in temporary_sanctions}
        suitable_guilds = bot_guilds & sanctions_guilds
        
        if guilds_to_remove := sanctions_guilds - suitable_guilds:
            query = f"""DELETE FROM {self.plugin_name}_sanctions
                        WHERE guild_id IN ({','.join('?'*len(guilds_to_remove))})"""
            async with db:
                await db.execute(query, guilds_to_remove)
            
        tasks = [
            self.shedule_sanction(*sanction)
            for sanction in temporary_sanctions
            if sanction[0] in suitable_guilds
        ]
        if tasks:
            await asyncio.gather(*tasks)
        
    async def set_log_channel(self, channel: discord.TextChannel) -> None:
        guild = channel.guild
        db = self.bot.asyncdb
        query = f"SELECT log_channel FROM {self.plugin_name} WHERE guild_id=?"
        async with db.execute(query, (guild.id,)) as cursor:
            result = await cursor.fetchone()
        if result:
            query = f"UPDATE {self.plugin_name} SET log_channel=? WHERE guild_id=?"
        else:
            query = f"INSERT INTO {self.plugin_name} (log_channel, guild_id) VALUES (?, ?)"
        async with db:
            await db.execute(query, (channel.id, guild.id,))
    
    async def get_log_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        db = self.bot.asyncdb
        query = f"SELECT log, log_channel FROM {self.plugin_name} WHERE guild_id=?"
        async with db.execute(query, (guild.id,)) as cursor:
            if not (result := await cursor.fetchone()):
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
        db = self.bot.asyncdb
        query = f"SELECT mute_role FROM {self.plugin_name} WHERE guild_id=?"
        async with db.execute(query, (guild.id,)) as cursor:
            result = await cursor.fetchone()
        if result and (mute_role := guild.get_role(result[0])):
            self.bot.loop.create_task(self.setup_mute_role(mute_role))
            return mute_role
        permissions = discord.Permissions(**self.mute_kwargs)
        mute_role = await guild.create_role(name="Mute", permissions=permissions,
                                            color=discord.Color.dark_red())
        async with db:
            query = f"INSERT INTO {self.plugin_name} (guild_id, mute_role) VALUES (?, ?)"
            await db.execute(query, (guild.id, mute_role.id,))
        self.bot.loop.call_soon(asyncio.ensure_future, self.setup_mute_role(mute_role))
        return mute_role
            
    async def get_warns(self, guild: discord.Guild, user: discord.User) -> tuple[int, int, int, float, str | None]:
        db = self.bot.asyncdb
        query = f"SELECT * FROM {self.plugin_name}_warns WHERE guild_id=? AND member_id=?"
        async with db.execute(query, (guild.id, user.id,)) as cursor:
            return await cursor.fetchall()
    
    # CAT: Events
    
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
        if not (log_channel := log_channel or await self.get_log_channel(guild)):
            return
        if not lang:
            lang = await self.get_lang(guild)
        
        description = lang.ON_KICK_DESCRIPTION.format(
            member=member, mod=moderator, reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_KICK_TITLE, user=member,
                         description=description, color=discord.Color.red())
        await log_channel.send(embed=embed)
    
    @discord.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild
        if not (log_channel := await self.get_log_channel(guild)):
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
        if not (log_channel := log_channel or await self.get_log_channel(guild)):
            return
        if not lang:
            lang = await self.get_lang(guild)
        
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
        db = self.bot.asyncdb
        query = f"""INSERT INTO {self.plugin_name}_sanctions (guild_id, user_id, mod_id, timestamp, reason)
                    VALUES (?, ?, ?, ?, ?)"""
        async with db:
            await db.execute(query, (guild.id, user.id, moderator.id, timestamp, reason))
        await self.shedule_sanction(guild.id, user.id, SanctionType.tempban, timestamp)
                 
        if not (log_channel := log_channel or await self.get_log_channel(guild)):
            return
        if not lang:
            lang = await self.get_lang(guild)
        
        duration = secs_to_humain(time.time() - timestamp)
        description = lang.ON_TEMPBAN_DESCRIPTION.format(
            user=user, mod=moderator, duration=duration,
            reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_TEMPBAN_TITLE, user=user,
                         description=description, color=discord.Color.greyple())
        await log_channel.send(embed=embed)

    @discord.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        if not (log_channel := await self.get_log_channel(guild)):
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
        if not (log_channel := log_channel or await self.get_log_channel(guild)):
            return
        if not lang:
            lang = await self.get_lang(guild)
        
        description = lang.ON_UNBAN_DESCRIPTION.format(
            user=user, mod=moderator, reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_UNBAN_TITLE, user=user,
                         description=description, color=discord.Color.greyple())
        await log_channel.send(embed=embed)

    @discord.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        if not (log_channel := await self.get_log_channel(guild)):
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
        db = self.bot.asyncdb
        query = f"""INSERT INTO {self.plugin_name}_warns (guild_id, member_id, mod_id, time, reason)
                    VALUES (?, ?, ?, ?, ?)"""
        async with db:
            await db.execute(query, (guild.id, member.id, moderator.id, reason))
            
        if not (log_channel := log_channel or await self.get_log_channel(guild)):
            return
        if not lang:
            lang = await self.get_lang(guild)
        if not warns:
            warns = len(await self.get_warns(guild, member))
        
        description = lang.ON_WARN_DESCRIPTION.format(user=member, mod=moderator, reason=reason)
        embed = LogEmbed(title=lang.ON_WARN_TITLE.format(warns=warns), user=member,
                         description=description, color=discord.Color.orange())
        await log_channel.send(embed=embed)
        
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
        if not (log_channel := log_channel or await self.get_log_channel(guild)):
            return
        if not lang:
            lang = await self.get_lang(guild)
            
        description = lang.ON_PURGE_USER_DESCRIPTION if user else lang.ON_PURGE_CHANNEL_DESCRIPTION
        description = description.format(user=user, mod=moderator, messages=messages,
                                         reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_WARN_TITLE, user=user,
                         description=description, color=discord.Color.yellow())
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
            db = self.bot.asyncdb
            query = f"""INSERT INTO {self.plugin_name}_sanctions (guild_id, user_id, type)
                        VALUES (?, ?, ?, ?)"""
            async with db:
                await db.execute(query, (guild.id, member.id, SanctionType.mute,))
    
        if not (log_channel := log_channel or await self.get_log_channel(member.guild)):
            return
        if not lang:
            lang = await self.get_lang(member.guild)
            
        description = lang.ON_MUTE_DESCRIPTION.format(
            member=member, mod=moderator, reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_MUTE_TITLE, member=member,
                         description=description, color=discord.Color.dark_red())
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
        db = self.bot.asyncdb
        query = f"""INSERT INTO {self.plugin_name}_sanctions (guild_id, user_id, mod_id, timestamp, reason)
                    VALUES (?, ?, ?, ?, ?)"""
        async with db:
            await db.execute(query, (guild.id, member.id, moderator.id, timestamp, reason))
        await self.shedule_sanction(guild.id, member.id, SanctionType.tempmute, timestamp)
                 
        if not (log_channel := log_channel or await self.get_log_channel(guild)):
            return
        if not lang:
            lang = await self.get_lang(guild)
        
        duration = secs_to_humain(time.time()-timestamp)
        description = lang.ON_TEMPMUTE_DESCRIPTION.format(
            member=member, mod=moderator, duration=duration,
            reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_TEMPMUTE_TITLE, member=member,
                         description=description, color=discord.Color.greyple())
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
            async with self.bot.asyncdb as db:
                query = f"""DELETE FROM {self.plugin_name}_sanctions
                            WHERE guild_id=? AND user_id=? AND type=?"""
                await db.execute(query, (guild.id, member.id, SanctionType.mute))
        
        if not (log_channel := log_channel or await self.get_log_channel(guild)):
            return
        if not lang:
            lang = await self.get_lang(guild)
        
        description = lang.ON_UNMUTE_DESCRIPTION.format(
            member=member, mod=moderator, reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_UNMUTE_TITLE, member=member,
                         description=description, color=discord.Color.greyple())
        await log_channel.send(embed=embed)
        
    @discord.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        db = self.bot.asyncdb
        query = f"""SELECT id FROM {self.plugin_name}_sanctions
                    WHERE guild_id=? AND user_id=? AND type IN (?, ?)"""
        async with db.execute(query, (guild.id, member.id, SanctionType.mute, SanctionType.tempmute)) as cursor:
            if not await cursor.fetchone():
                return
        
        mute_role = await self.get_mute_role(guild)
        await member.add_roles(mute_role)
        await self.on_mute(member, self.bot.user, "User joined while he was muted.", update_from_db=False)
    
    # CAT: Commands
    
    @bridge.bridge_command(
        name="logs",
        description="Changes the log channel.",
        options=[discord.Option(discord.TextChannel, name="channel", description="The log channel.")]
    )
    @bridge.has_permissions(manage_channels=True)
    @commands.cooldown(2, 15, commands.BucketType.guild)
    async def _set_log_channel(self, ctx: bridge.BridgeApplicationContext, channel: discord.TextChannel) -> None:
        lang: English = await self.get_lang(ctx)
        
        await self.set_log_channel(channel)
        
        description = lang.SET_LOG_CHANNEL_DESCRIPTION.format(channel=channel)
        embed = discord.Embed(title=lang.SET_LOG_CHANNEL_TITLE, description=description,
                              color=discord.Color.green())
        await ctx.respond(embed=embed)
        

def setup(bot):
    bot.add_cog(Moderation(bot))