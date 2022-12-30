import discord

from src import PluginCog, Shibbot

from . import English


class SanctionType:
    warn = "warn"
    warn_delete = "delwarn"
    clear = purge = "clear"
    mute = "mute"
    temp_mute = "tmute"
    unmute = "unmute"
    kick = yeet = "kick"
    ban = "ban"
    multi_ban = "mban"
    soft_ban = "sban"
    temp_ban = "tban"
    unban = "unban"


class Moderation(PluginCog):
    
    def __init__(self, bot):
        self.bot: Shibbot = bot
        super().__init__(
            plugin_name="mod",
            guild_only=True,
            bot=bot,
            name={"en": "Moderation", "fr": "Modération"},
            description={"en": "Helps you moderating your server."},
            languages={"en": English,}, emoji="👮"
        )

        self.bot.cursor.execute(f"CREATE TABLE IF NOT EXISTS sanctions (id TEXT PRIMARY_KEY, guild_id INTEGER, user_id INTEGER, type TEXT, duration DATETIME)")
        self.bot.cursor.execute("CREATE TABLE IF NOT EXISTS warns(id TEXT PRIMARY_KEY, guild_id INTEGER, user_id INTEGER, reason TEXT, date DATETIME, mod_id INTEGER)")
        self.bot.db.commit()


    async def mod_log(self, guild: discord.Guild, method_used):
        lang = await self.get_lang(guild)

        

    
