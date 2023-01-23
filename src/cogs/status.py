from asyncio import sleep as async_sleep
from random import choice
from discord import Game, Activity, ActivityType, Status
from discord.ext import tasks

from src import __version__ as version, __github__ as __github__
from src.core import Shibbot
from src.models import BaseCog


LOOP_TIME = 60  # In seconds

def setup(bot):
    bot.add_cog(ChangeActivity(bot))

class ChangeActivity(BaseCog):
    def __init__(self, bot):
        self.bot: Shibbot = bot
        super().__init__(hidden=True)

        self.bot_statutes = [f"version v{version}", "/help", "{latency}ms", "{guilds} servers", "{users} users", __github__]
        self.watching_statutes = [
            "after the guy who stole my milk", "you.", "submissions on Reddit", "the end of the world", "ur mama", "inside your soul",
            "Breaking Bed", "hentai", "your brain cells go", "boTs hAve riGhtS tOo", "JESSE, WE NEED TO COOK JESSE",
            "doesn't dwayne johnson kinda look like the rock ???", "Mandela Catalogue", "Sr Pelo", "having an existential crisis",
            "(Mg, Fe)₇Si₈O₂₂(OH)₂", "a mongo on a fork", "at the end of the day it's not that funny is it",
        ]
        self.listening_statutes = [
            "Jetpack Joyride Main Theme", "Kahoot Lobby Music", "Never Gonna Give You Up", "wenomechainsama", "Bad Computer",
            "🗿", "EEEAAAOOO", "ShibASMR", "A SOUNGUS AMONGUS", "Bad Apple", "skrr shtibi shtipi dob dop yes yes jes shtip",
            "Petit Biscuit (my beloved)",
        ]
        self.game_statutes = [
            "Sea of Shibbs", "Five Nights at Doggo's", "Fortinaiti ila Babaji ?", "Amogus ඞ", "ROBLOSS", "Cyberpunk 2069", "Minecwaft",
            "Shiba Horizon 5", "Portel 2", "Genshit Impact", "I'll have 2 number 9", "AMONGOS", "Celeste", "Endacopia", "OneShot", "🤸🦽🏌️",
        ]

    async def when_fully_ready(self):
        await async_sleep(10)
        self.change_activity.start()

    @tasks.loop(seconds=LOOP_TIME)
    async def change_activity(self):
        if self.bot.latency == float('inf'):
            return # Avoiding OverflowError
        latency = int(self.bot.latency * 1000)

        if choice((True, False)):
            activity = Activity(type=ActivityType.watching, name=choice(self.bot_statutes).format(latency=latency,
                                                                                                  guilds=len(self.bot.guilds),
                                                                                                  users=len(self.bot.users)))
        else:
            activity = choice(
                (Activity(type=ActivityType.watching, name=choice(self.watching_statutes)),
                 Activity(type=ActivityType.listening, name=choice(self.listening_statutes)),
                 Game(name=choice(self.game_statutes)))
            )

        status = Status.online if latency < 300 else Status.idle
        await self.bot.change_presence(status=status, activity=activity)
