import datetime
import sqlite3
import os as sus

import discord
from discord.ext import commands

import utils
from utils import Reddit, fl

__author__ = "JeanTheShiba"
__version__ = "0.3"


def get_prefix(client, ctx) -> str:
    """Gets the prefix of a server."""
    try:
        if ctx.guild:
            client.cursor.execute(
                "SELECT prefix FROM guilds WHERE guild_id=?",
                (ctx.guild.id)
            )
            prefix = client.cursor.fetchone()
            if not prefix:
                raise Exception
            return prefix[0]
        raise Exception
    except:
        return client.default_prefix


class Shibbot(commands.Bot):
    """Subclass of `commands.Bot`, our little Shibbot :3."""

    def __init__(
        self,
        test_mode: bool = False,
        *args,
        **kwargs,
    ):
        self.version = __version__
        self.test_mode = test_mode
        self.config = utils.load("config.json")
        self.init_at = datetime.datetime.utcnow()
        #self.website_url = "shibbot.xyz"
        self.fl = fl

        self.db_path = "database.sqlite"
        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()
        print(f"[+] Connected to Database. Located at /{self.db_path}")
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS guilds(guild_id INTEGER PRIMARY KEY, prefix TEXT, lang TEXT)")
        self.db.commit()

        self.discord_conf = self.config["discord"]
        self.default_prefix = "$"
        self.default_language = "en"
        self.invite_bot_url = None
        self.token = self.discord_conf["release"] if not test_mode else self.discord_conf["snapshot"]
        self.bot_is_alive = None
        super().__init__(
            command_prefix=get_prefix,
            owner_id=380044496370532353,
            allowed_mentions=discord.AllowedMentions(
                roles=False,
                users=True,
                everyone=False,
                replied_user=False
            ),
            intents=discord.Intents.all(),
            case_insensitive=True,
            activity=discord.Streaming(
                name="connecting...",
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            ),
            *args, **kwargs
        )
        super().remove_command("help")

        self.reddit_conf = self.config["reddit"]
        self.reddit = Reddit(
            loop=self.loop,
            client_id='eHjvFtZ3cYzNbRYyxs4akA',
            client_secret=self.reddit_conf["client_secret"],
            user_agent='shibbot',
            username="JeanTheShiba",
            password=self.reddit_conf["password"],
        )

        print(f"   ----------------------------\n[+] Loading cogs...")
        for filename in sus.listdir("./cogs"):
            if filename.endswith(".py"):
                cogname = filename[:-3]
                try:
                    self.load_extension(f"cogs.{cogname}")
                except Exception as e:
                    print(
                        f"[x] Could not load '{cogname}' : ({type(e).__name__}: {e})")

    def fetch_guild(self, guild: discord.Guild):
        """Used to fetch a guild's data or insert a guild into the guild's table."""
        self.cursor.execute(
            f"SELECT * FROM guilds WHERE guild_id={guild.id}")
        data = self.cursor.fetchone()
        if not data:
            self.cursor.execute(
                "INSERT INTO guilds (guild_id, prefix, lang) VALUES (?,?,?)",
                (guild.id, self.default_prefix, self.default_language)
            )
            self.db.commit()
        return data

    def _get_prefix(self, ctx: commands.Context) -> str:
        return get_prefix(self, ctx)

    def get_lang(self, ctx: commands.Context) -> str:
        """Gets the langage of a server."""
        try:
            if ctx.guild or isinstance(ctx, discord.Guild):
                self.cursor.execute(
                    "SELECT lang FROM guilds WHERE guild_id=?",
                    (ctx.guild.id,)
                )
                lang = self.cursor.fetchone()
                if not lang:
                    raise Exception
                return lang[0]
            raise Exception
        except:
            return self.default_language

    async def on_guild_join(self, guild: discord.Guild):
        """Triggered when the bot joins a guild"""
        print(f"- Joined guild {guild.name} ({guild.id})")

    async def on_guild_remove(self, guild: discord.Guild):
        """Triggered when the bot leaves a guild."""
        print(f"- Left {guild.name} ({guild.id})")

    async def on_ready(self):
        """Runs when the bot has successfully connected to Discord API"""
        print(
            f"   ----------------------------\n[+] Ready. \n[-] Connected as : {super().user}\n[-] Id : {super().user.id}")
        if self.bot_is_alive is None:
            self.invite_bot_url = f"https://discord.com/api/oauth2/authorize?client_id={super().user.id}&permissions=8&scope=applications.commands%20bot"
        self.bot_is_alive = True

    async def on_resumed(self):
        print("[+] Bot reconnected.")
        self.bot_is_alive = True

    async def on_disconnect(self):
        """Says when the bot is disconnected."""
        if self.bot_is_alive != False:
            print("[x] Bot disconnected.")
            self.bot_is_alive = False

    def run(self):
        try:
            super().run(
                self.token,
                reconnect=True
            )
        except Exception as e:
            self.db.close()
            print(f"[-] Program finished : ({type(e).__name__}: {e})")


def start():
    """Starts the bot with a beautiful ASCII art."""
    print(
        f" ________________________________\n|░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|\n|░░░█▀▀░█░█░▀█▀░█▀▄░█▀▄░█▀█░▀█▀░░|\n"
        f"|░░░▀▀█░█▀█░░█░░█▀▄░█▀▄░█░█░░█░░░|\n|░░░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░░▀░░░|\n"
        f"|░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|\n --------------------------------\n   ----------------------------\n[-] "
        f"Version : {__version__}")
    shibbot = Shibbot(test_mode=True)
    shibbot.run()


if __name__ == "__main__":
    start()

# Why is there a burger in this folder I can't delete it ?
