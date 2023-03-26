import discord
import asyncio
from datetime import datetime

from src.core import Shibbot
from src.models import PluginCog
from src.constants import CACHE_PATH


PLUGIN_NAME = "mod"
SUS_DOMAINS_FP = CACHE_PATH + "/sus_links.json"


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
        if user:
            self.set_author(name=title, icon_url=user.avatar)
        else:
            self.title = title
        self.timestamp = datetime.utcnow()
        super().__init__(*args, **kwargs)


class Moderation(PluginCog):
    def __init__(self, bot):
        self.bot: Shibbot = bot
        super().__init__(
            plugin_name=PLUGIN_NAME,
            name={"en": "Moderation", "fr": "Modération"},
            description={"en": "Tools to moderate your server.", "fr": "Des outils pour modérer votre serveur."},
            languages={}, emoji="👮"
        )
        
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.plugin_name} (
            guild_id    INTEGER PRIMARY KEY,
            log_channel INTEGER,
            mute_role   INTEGER
        );
        CREATE TABLE IF NOT EXISTS sanctions (
            guild_id    INTEGER NOT NULL,
            user_id     INTEGER NOT NULL,
            type        TEXT NOT NULL,
            duration    REAL NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_guild_sanctions ON sanctions (guild_id);
        CREATE TABLE IF NOT EXISTS warns (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id    INTEGER NOT NULL,
            user_id     INTEGER NOT NULL,
            mod_id      INTEGER NOT NULL,
            time        REAL NOT NULL,
            reason      TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_guild_warns ON warns (guild_id)
        """
        self.bot.db.executescript(query) # VER: v1.0.0
        self.bot.db.commit()
    
    @discord.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await asyncio.sleep(0.5)
        found_entry = None
        async for entry in member.guild.audit_logs(action=discord.AuditLogAction.kick, limit=50):
            if entry.target == member:
                found_entry = entry
                break
        if found_entry and not self.bot.user != found_entry.user:
            pass
            # TODO: Log

    @discord.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        await asyncio.sleep(0.5)
        found_entry = None
        async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=50):
            if entry.target == user:
                found_entry = entry
                break
        if found_entry and self.bot.user != found_entry.user:
            pass
            # TODO: Log

    @discord.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        await asyncio.sleep(0.5)
        found_entry = None
        async for entry in guild.audit_logs(action=discord.AuditLogAction.unban, limit=50):
            if entry.target.id == user.id:
                found_entry = entry
                break
        if found_entry:
            pass
            # TODO: Log

    @discord.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        # TODO: Remove sanctions from database
        pass