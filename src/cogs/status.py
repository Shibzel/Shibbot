import asyncio
import random
import datetime

import discord
from discord.ext import tasks, commands

from src import Shibbot, __version__ as version


LOOP_TIME = 60  # In seconds


def setup(bot):
    bot.add_cog(ChangeActivity(bot))


class ChangeActivity(commands.Cog):
    def __init__(self, bot):
        self.bot: Shibbot = bot

        self.bot_statutes = [f"version v{version}", "/help", "{latency}ms", "{guilds} servers", "{users} users",]
        self.watching_statutes = ["after the guy who stole my milk", "you.", "submissions on Reddit", "the end of the world", "ur mama", "inside your soul",
                                  "it's Morbin time", "Breaking Bed", "hentai", "your brain cells go", "boTs hAve riGhtS tOo", "JESSE, WE NEED TO COOK JESSE",
                                  "doesn't dwayne johnson kinda look like the rock ???", "Mandela Catalogue", "Sr Pelo", "having an existential crisis",]
        self.listening_statutes = ["Jetpack Joyride Main Theme", "Kahoot Lobby Music", "Never Gonna Give You Up", "wenomechainsama", "Bad Computer",
                                   "🗿", "EEEAAAOOO", "ShibASMR", "A SOUNGUS AMONGUS", "Bad Apple", "skrr shtibi shtipi dob dop yes yes jes shtip",]
        self.game_statutes = ["Sea of Shibbs", "Five Nights at Doggo's", "Fortinaiti ila Babaji ?", "Amogus ඞ", "ROBLOSS",
                              "Cyberpunk 2069", "HEE HEE HE HA", "Minecwaft", "Shiba Horizon 5", "Portel 2", "Underfail", "Genshit Impact", "Off",
                              "Absolutely accurate battle simulator", "I'll have 2 number 9", "AMONGOS", "Celeste", "Endacopia", "OneShot", "🤸🏌️"]

        self.bot.loop.create_task(self.start_status_loop())
        self.halloween_statutes = ["it is spooky month !!", "🎃", "OOGA BOOGA 🧟‍♀️", "Boo 👻", "oh man i'm dead 💀⚰️"]
        self.bot.loop.create_task(self.monthly_calender_event(self.halloween_statutes, month=10))
        self.chrismas_statutes = ["chrismas status",]
        self.bot.loop.create_task(self.monthly_calender_event(self.chrismas_statutes, month=12))

    async def monthly_calender_event(self, statutes: list, month: int,):
        while True:
            # TODO: improve the code below.
            now = datetime.datetime.utcnow()
            if now.month == month:
                sleep = 60
            elif now.month > month:
                next_date = datetime.datetime(year=now.year+1, month=month, day=1)
                sleep = (next_date-now).total_seconds()
            elif now.month < month:
                next_date = datetime.datetime(year=now.year, month=month, day=1)
                sleep = (next_date-now).total_seconds()
            await asyncio.sleep(sleep)

            self.bot_statutes.extend(statutes)
            after_sleep_now = datetime.datetime.utcnow()
            year, month = now.year, now.month
            if month == 12:
                year, month = year+1, 1
            end_date = datetime.datetime(year=year, month=month, day=1)
            await asyncio.sleep((end_date-after_sleep_now).total_seconds())
            for status in statutes:
                self.bot_statutes.remove(status)

    async def start_status_loop(self):
        while not self.bot.is_alive:
            await asyncio.sleep(1)
        await asyncio.sleep(10)
        self.change_activity.start()

    @tasks.loop(seconds=LOOP_TIME)
    async def change_activity(self):
        if self.bot.latency == float('inf'):
            return # Avoiding OverflowError
        latency = int(self.bot.latency * 1000)

        if random.choice((True, False)):
            activity = discord.Activity(type=discord.ActivityType.watching,
                                        name=random.choice(self.bot_statutes).format(latency=latency, guilds=len(self.bot.guilds), users=len(self.bot.users)))
        else:
            activity = random.choice(
                (discord.Activity(type=discord.ActivityType.watching, name=random.choice(self.watching_statutes)),
                 discord.Activity(type=discord.ActivityType.listening, name=random.choice(self.listening_statutes)),
                 discord.Game(name=random.choice(self.game_statutes)))
            )

        status = discord.Status.online if latency < 300 else discord.Status.idle

        await self.bot.change_presence(status=status, activity=activity)
