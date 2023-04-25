import asyncio
import random
from discord import Game, Activity, ActivityType, Status
from discord.ext import tasks

from src import __version__ as version, __github__ as __github__
from src.core import Shibbot
from src.models import BaseCog
from src.constants import OFFICIAL_SHIBBOT_INSTANCES


LOOP_TIME = 60  # In seconds

def setup(bot):
    bot.add_cog(ChangeActivity(bot))

class ChangeActivity(BaseCog):
    def __init__(self, bot: Shibbot):
        self.bot = bot
        super().__init__(hidden=True)

        self.bot_statutes = [f"version v{version}", "{guilds} servers", "{users} users",]
        if self.bot.user.id in OFFICIAL_SHIBBOT_INSTANCES:
            self.bot_statutes.append("shibbot.ml/invite")
        self.watching_statutes = [
            "after the guy who stole my milk", "you.", "submissions on Reddit",
            "the end of the world", "ur mama", "inside your soul", "(Mg, Fe)₇Si₈O₂₂(OH)₂",
            "Breaking Bed", "hentai", "your brain cells go", "boTs hAve riGhtS tOo",
            "JESSE, WE NEED TO COOK JESSE", "Sr Pelo", "having an existential crisis",
            "doesn't dwayne johnson kinda look like the rock ???", "Mandela Catalogue",
            "at the end of the day it's not that funny is it", "a mongo on a fork",
        ]
        self.listening_statutes = [
            "Jetpack Joyride Main Theme", "Kahoot Lobby Music", "Never Gonna Give You Up",
            "wenomechainsama", "Bad Computer", "🗿", "EEEAAAOOO", "ShibASMR", "A SOUNGUS AMONGUS",
            "Bad Apple", "skrr shtibi shtipi dob dop yes yes jes shtip", "Petit Biscuit (my beloved)",
        ]
        self.game_statutes = [
            "Sea of Shibbs", "Five Nights at Doggo's", "Fortinaiti ila Babaji ?", "Amogus ඞ",
            "ROBLOSS", "Cyberpunk 2069", "Minecwaft", "OneShot", "🤸🦽🏌️", "Endacopia",
            "Shiba Horizon 5", "Portel 2", "Genshit Impact", "I'll have 2 number 9", "AMONGOS",
            "Celeste",
        ]

    async def when_ready(self):
        await asyncio.sleep(10)
        self.logger.debug(f"Updating status every {LOOP_TIME} sec.")
        self.change_activity.start()

    @tasks.loop(seconds=LOOP_TIME)
    async def change_activity(self):
        if self.bot.latency == float('inf'):
            return # Avoiding OverflowError
        latency = int(self.bot.latency * 1000)
        
        name = "/help • {}"
        if random.randint(0, 2): # 1/3 chance
            activity = Activity(type=ActivityType.watching,
                                name=name.format(random.choice(self.bot_statutes).format(
                                    latency=latency,
                                    guilds=len(self.bot.guilds),
                                    users=len(self.bot.users))))
        else:
            activity = random.choice(
                (Activity(type=ActivityType.watching,
                          name=(random.choice(self.watching_statutes))),
                 Activity(type=ActivityType.listening,
                          name=random.choice(self.listening_statutes)),
                 Game(name=random.choice(self.game_statutes)))
            )
            
        status = Status.online if latency < 300 else Status.idle
        await self.bot.change_presence(status=status, activity=activity)
