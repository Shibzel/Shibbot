import asyncio
import random

import discord
from discord.ext import tasks, commands

from src import Shibbot, __version__ as version


LOOP_TIME = 60  # In seconds


def setup(bot):
    bot.add_cog(ChangeActivity(bot))


class ChangeActivity(commands.Cog):
    
    def __init__(self, bot):
        self.bot: Shibbot = bot

        self.watching_statutes = ["after the guy who stole my milk", "you.", "submissions on Reddit", "the end of the world", "ur mama", "inside your soul",
                                  "it's Morbin time", "Breaking Bed", "hentai", "your brain cells go", "boTs hAve riGhtS tOo", "JESSE, WE NEED TO COOK JESSE",
                                  "doesn't dwayne johnson kinda looks like the rock ???", "Mandela Catalogue", "Sr Pelo", "having an existential crisis",]
        self.listening_statutes = ["Jetpack Joyride Main Theme", "Kahoot Lobby Music", "Never Gonna Give You Up", "wenomechainsama", "Bad Computer",
                                   "🗿", "EEEAAAOOO", "ShibASMR", "A SOUNGUS AMONGUS", "Bad Apple", "skrr shtibi shtipi dob dop yes yes jes shtip",]
        self.game_statutes = ["Sea of Shibbs", "Five Nights at Doggo's", "Fortinaiti ila Babaji ?", "Amogus ඞ", "ROBLOSS",
                              "Cyberpunk 2069", "HEE HEE HE HA", "Minecwaft", "Shiba Horizon 5", "Portel 2", "Underfail", "Genshit Impact", "Off",
                              "Absolutely accurate battle simulator", "I'll have 2 number 9", "AMONGOS", "Celeste", "Endacopia", "OneShot",]


    @discord.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(10)
        self.change_activity.start()


    @tasks.loop(seconds=LOOP_TIME)
    async def change_activity(self):
        if self.bot.latency == float('inf'):
            return # Avoiding OverflowError
        latency = int(self.bot.latency * 1000)

        if random.choice((True, False)):
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name=random.choice((f"version v{version}", "/help", f"{latency}ms", f"{len(self.bot.guilds)} servers", f"{len(self.bot.users)} users",)))
        else:
            activity = random.choice((
                discord.Activity(
                    type=discord.ActivityType.watching,
                    name=random.choice(self.watching_statutes)),
                discord.Activity(
                    type=discord.ActivityType.listening,
                    name=random.choice(self.listening_statutes)),
                discord.Game(
                    name=random.choice(self.game_statutes))))

        status = discord.Status.online if latency < 300 else discord.Status.idle

        await self.bot.change_presence(status=status, activity=activity)
