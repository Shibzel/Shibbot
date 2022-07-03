import asyncio
import random

import discord
from discord.ext import commands, tasks

from bot import Shibbot


def setup(client):
    client.add_cog(ChangeActivity(client))


class ChangeActivity(commands.Cog):
    def __init__(self, client):
        self.client: Shibbot = client
        self.activity_is_looping = False

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.activity_is_looping:
            await asyncio.sleep(5.5)
            self.change_activity.start()
            self.activity_is_looping = True

    @tasks.loop(seconds=30)
    async def change_activity(self):
        if random.choice((True, False)):
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name=random.choice(
                    (f"the version v{self.client.version}",  # self.client.website_url,
                        f"over {len(self.client.guilds)} servers", f"over {len(self.client.users)} users",
                        "/help", "shiBbot is bacc !11§!!")
                )
            )
        else:
            activity = random.choice(
                (
                    discord.Activity(
                        type=discord.ActivityType.watching,
                        name=random.choice(
                            ("after the guy who stole my milk", "you.", "submissions on Reddit", "the end of the world", "ur mama",
                                "inside your soul", "to but rare fish", "mee6.xyz, nah i'm joking, i hope i had a website tho",
                                "hentai", "your brain cells go")
                        )
                    ),
                    discord.Activity(
                        type=discord.ActivityType.listening,
                        name=random.choice(
                            ("Jetpack Joyride Main Theme", "Kahoot Lobby Music",
                                "goofy ahh sound - goofy ahh dj", "Rick Astley - Never Gonna Give You Up", "wenomechainsama")
                        )
                    ),
                    discord.Game(
                        name=random.choice(
                            ("Sea of Shibbs", f"Five Nights at Doggo's {random.randint(1, 5)}", "Fortinaiti ila Babaji ?", "Amogus ඞ",
                             "ROBLOSS", "Shibapunk 2077", "HEE HEE HE HA", "Minecraft 2.0", "Shiba Horizon 5", "Portel 2")
                        )
                    )
                )
            )
        await self.client.change_presence(
            status=discord.Status.online if self.client.latency *
            1000 < 400 else discord.Status.idle,
            activity=activity
        )
