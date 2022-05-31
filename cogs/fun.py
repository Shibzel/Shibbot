import discord
from discord.ext import commands, tasks

import utils
from bot import Shibbot

client = None


def setup(_client):
    global client
    client = _client
    client.add_cog(Fun(client))


def plugin_is_enabled():
    async def predicate(ctx):
        if ctx.guild:
            client.cursor.execute(
                f"SELECT enabled FROM fun_plugin WHERE guild_id=?",
                (ctx.guild.id,)
            )
            enabled = client.cursor.fetchone()
            if enabled:
                enabled = enabled[0]
            return enabled
        else:
            return True
    return commands.check(predicate)


class Fun(commands.Cog):
    def __init__(self, client):
        self.client: Shibbot = client
        self.reddit: utils.Reddit = self.client.reddit

        self.client.cursor.execute(
            "CREATE TABLE IF NOT EXISTS fun_plugin (guild_id INTEGER PRIMARY KEY, enabled BOOLEAN)")

    for i in ("shibes", "cats", "birds", "foxes", "memes", "nsfw_memes"):
        try:
            setattr(self, i, utils.load(f"cache/{i}.json"))
        except (Exception,) as e:
            setattr(self, i, None)
            print(f"[x] Failed loading {i}.json, the command associed to it won't work until it got updated : {str(e)}")

    @tasks.loop(hours=10)
    async def update_shibe_online(self):
        async def update(i):
            try:
                urls = await utils.fetch_from_urls([f"https://shibe.online/api{i}?count=100&urls=true&httpsUrls=true"]*10)
                setattrs(self, i, urls)
                utils.dump(urls, f"cache/{i}.json")
                print(f"[+] Sucessfully updated {i}.")
            except Excetion as e:
                print(f"[x] Failed while trying to update {i} : {str(e)}")
        tasks = [update(i) for i in ["shibes", "cats", "birds"]]
        await asyncio.gather(*tasks)
