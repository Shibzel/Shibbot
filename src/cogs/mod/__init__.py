import discord
import asyncio
from datetime import datetime

from src.core import Shibbot
from src.models import PluginCog

from .lang import English


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
            duration    REAL NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_guild
            ON {self.plugin_name}_sanctions (guild_id, user_id);
        CREATE TABLE IF NOT EXISTS {self.plugin_name}_warns (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id    INTEGER NOT NULL,
            member_id   INTEGER NOT NULL,
            mod_id      INTEGER NOT NULL,
            time        REAL NOT NULL,
            reason      TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_guild
            ON {self.plugin_name}_warns (guild_id, user_id)
        """
        self.bot.db.executescript(query) # VER: v1.0.0
        self.bot.db.commit()
    
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
    
    # CAT: Events
    
    async def _find_entry(
            self,
            guild: discord.Guild,
            user: discord.Guild,
            action: discord.AuditLogAction
        ) -> discord.AuditLogEntry | None:
        async for entry in guild.audit_logs(action=action, limit=50):
            if entry.target == user:
                if user == self.bot.user:
                    return None
                return entry
    
    async def on_kick(
            self,
            member: discord.Member,
            moderator: discord.Member,
            reason: str = None,
            lang: English = None,
            log_channel: discord.TextChannel = None,
        ):
        if not (log_channel := log_channel or await self.get_log_channel(member.guild)):
            return
        if not lang:
            lang = await self.get_lang(member.guild)
        
        description = lang.ON_KICK_DESCRIPTION.format(
            member=member, mod=moderator, reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_KICK_TITLE, user=member,
                         description=description, color=discord.Color.red())
        await log_channel.send(embed=embed)
    
    @discord.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if not (log_channel := await self.get_log_channel(member.guild)):
            return
        await asyncio.sleep(0.5)
        if found_entry := await self._find_entry(member.guild, member, discord.AuditLogAction.kick):
            await self.on_kick(member, found_entry.user, found_entry.reason, log_channel=log_channel)

    async def on_ban(
            self,
            user: discord.User,
            moderator: discord.Member,
            reason: str = None,
            lang: English = None,
            log_channel: discord.TextChannel = None,
        ):
        if not (log_channel := log_channel or await self.get_log_channel(moderator.guild)):
            return
        if not lang:
            lang = await self.get_lang(moderator.guild)
        
        description = lang.ON_BAN_DESCRIPTION.format(
            user=user, mod=moderator, reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_BAN_TITLE, user=user,
                         description=description, color=discord.Color.dark_red())
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
        ):
        if not (log_channel := log_channel or await self.get_log_channel(moderator.guild)):
            return
        if not lang:
            lang = await self.get_lang(moderator.guild)
        
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
            
    async def get_warns(self, guild: discord.Guild, user: discord.User) -> tuple[int, int, int, float, str | None]:
        db = self.bot.asyncdb
        query = f"SELECT * FROM {self.plugin_name}_warns WHERE guild_id=? AND member_id=?"
        async with db.execute(query, (guild.id, user.id,)) as cursor:
            return await cursor.fetchall()
            
    async def on_warn(
            self,
            member: discord.Member,
            moderator: discord.Member,
            warns: int = None,
            reason: str = None,
            lang: English = None,
            log_channel: discord.TextChannel = None,
        ):
        guild = member.guild
        db = self.bot.asyncdb
        query = f"""INSERT INTO {self.plugin_name}_warns (guild_id, member_id, mod_id, time, reason)
                    VALUES (?, ?, ?, ?, ?)"""
        async with db:
            await db.execute(query, (guild.id, member.id, moderator.id, reason))
            
        if not (log_channel := log_channel or await self.get_log_channel(moderator.guild)):
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
            log_channel: discord.TextChannel = None,
        ):
        if not (log_channel := log_channel or await self.get_log_channel(channel.guild)):
            return
        if not lang:
            lang = await self.get_lang(channel.guild)
            
        description = lang.ON_PURGE_USER_DESCRIPTION if user else lang.ON_PURGE_CHANNEL_DESCRIPTION
        description = description.format(user=user, mod=moderator, messages=messages,
                                         reason=reason or lang.NO_REASON_PLACEHOLDER)
        embed = LogEmbed(title=lang.ON_WARN_TITLE, user=user,
                         description=description, color=discord.Color.yellow())
        await log_channel.send(embed=embed)
            
            
        
    
    # CAT: Commands
    
    pass

def setup(bot):
    bot.add_cog(Moderation(bot))