import asyncio
import random

import discord
from discord.ext import commands, tasks

from bot import Shibbot

LOOP_TIME = 30


def setup(client):
    client.add_cog(ChangeActivity(client))


class ChangeActivity(commands.Cog):
    """Loops the bot's activity every x seconds.
    This is separated from the rest so we don't have to reload an entire cog just to change the list of possible activities."""

    def __init__(self, client):
        self.client: Shibbot = client
        self.activity_is_looping = False

    @commands.Cog.listener()
    async def on_ready(self):
        self.member_count = len(self.client.users)
        if not self.activity_is_looping:
            await asyncio.sleep(5.5)
            self.change_activity.start()
            self.get_member_count.start()
            self.activity_is_looping = True

    @tasks.loop(hours=24)
    async def get_member_count(self):
        member_count = 0
        for guild in self.client.guilds:
            member_count += guild.approximate_member_count or guild.member_count
        self.member_count = member_count
        print(f"[+] Counted {self.member_count} members.")

    @tasks.loop(seconds=LOOP_TIME)
    async def change_activity(self):
        latency = round(self.client.latency * 1000, 2)

        if random.choice((True, False)):
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name=random.choice((f"the version v{self.client.version}", "/help", f"ping : {latency}ms",  # self.client.website_url,
                                    f"over {len(self.client.guilds)} servers", f"over {self.member_count} members",)))
        else:
            activity = random.choice((
                discord.Activity(
                    type=discord.ActivityType.watching,
                    name=random.choice(("after the guy who stole my milk", "you.", "submissions on Reddit", "the end of the world", "ur mama", "inside your soul",
                                        "it's Morbin time", "Breaking Bed", "hentai", "your brain cells go", "Bots have rights too", "JESSE, WE NEED TO COOK JESSE",
                                        "Firefox >>> Chrome"))),
                discord.Activity(
                    type=discord.ActivityType.listening,
                    name=random.choice(("Jetpack Joyride Main Theme", "Kahoot Lobby Music", "Never Gonna Give You Up", "wenomechainsama", "Bad Computer",
                                        "🗿",))),
                discord.Game(
                    name=random.choice(("Sea of Shibbs", f"Five Nights at Doggo's {random.randint(1, 6)}", "Fortinaiti ila Babaji ?", "Amogus ඞ", "ROBLOSS",
                                        "Cyberpunk 2069", "HEE HEE HE HA", "Minecwaft", "Shiba Horizon 5", "Portel 2", "Undertails", "Genshit Impact",
                                        "Absolutely accurate battle simulator", "I'll have 2 number 9", "Jerry's mod", "Celeste",)))))

        status = discord.Status.online if latency < 400 else discord.Status.idle

        await self.client.change_presence(status=status, activity=activity)
