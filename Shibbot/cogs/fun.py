import asyncio
from cmath import e
import random
import time

import discord
from discord.ext import commands, tasks

import utils
from utils import EmbedViewer
from bot import Shibbot

client = None


def setup(_client):
    global client
    client = _client
    client.add_cog(Fun(client))


def plugin_is_enabled():
    async def predicate(ctx):
        if ctx.guild:
            async with client.aiodb() as db:
                async with db.execute(
                    f"SELECT enabled FROM fun_plugin WHERE guild_id=?",
                    (ctx.guild.id,)
                ) as cursor:
                    enabled = await cursor.fetchone()
            if enabled:
                enabled = enabled[0]
            return enabled
        else:
            return True
    return commands.check(predicate)


class Fun(commands.Cog):
    def __init__(self, client):
        self.client: Shibbot = client

        self.shibes, self.cats, self.birds, self.memes, self.nsfw_memes = [], [], [], [], []

        self.client.cursor.execute(
            "CREATE TABLE IF NOT EXISTS fun_plugin (guild_id INTEGER PRIMARY KEY, enabled BOOLEAN)")
        self.client.db.commit()

        for i in ("shibes", "cats", "birds", "memes", "nsfw_memes"):
            try:
                setattr(self, i, utils.load(f"cache/{i}.json"))
            except (Exception,) as e:
                setattr(self, i, [])
                print(
                    f"[x] Failed loading {i}.json, the command associed to it won't work until it got updated : ({type(e).__name__}: {str(e)})")

        self.update_shibe_online.start()
        self.update_reddit_memes.start()

    @commands.Cog.listener()
    @plugin_is_enabled()
    async def on_message(self, message):
        if message.content == "(╯°□°）╯︵ ┻━┻":
            await message.reply("┬─┬ ノ( ゜-゜ノ)")

    @tasks.loop(hours=4)
    async def update_shibe_online(self):
        async def update(i):
            try:
                urls_list = await utils.get_from_urls([f"https://shibe.online/api/{i}?count=100&urls=true&httpsUrls=true"]*5)
                urls = []
                for list in urls_list:
                    urls += list
                urls = utils.filter_doubles(urls)
                setattr(self, i, urls)
                utils.dump(urls, f"cache/{i}.json")
                #print(f"[-] Sucessfully updated {i} ({len(urls)} images).")
            except Exception as e:
                print(
                    f"[x] Failed while trying to update {i} : ({type(e).__name__}: {str(e)})")
        start_time = time.time()
        tasks = [update(i) for i in ("shibes", "cats", "birds")]
        await asyncio.gather(*tasks)
        print(
            f"[+] All images updated (took {(time.time() - start_time):.2f} sec).")

    @tasks.loop(hours=12)
    async def update_reddit_memes(self):
        self.reddit: utils.Reddit = self.client.reddit()
        # For some reason this func uses A LOT of memory, (~60Mo -> ~300Mo of RAM). To prevent memory outage it must be fixed.
        memes_subs = ("memes", "meme", "History_memes", "HolUp", "dankmemes", "Memes_Of_The_Dank", "ProgrammerHumor", "shitposting",
                      "GenZMemes", "funny", "cursedmemes", "MemesIRL", "pcmemes", "holup", "blursedimages", "AdviceAnimals", "okbuddyretard")
        nsfw_memes_subs = ("hentaimemes", "NSFWMemes", "Offensivejokes",
                           "thensfwmemes", "IronicPornMemes", "NSFWMeme")

        async def get_filtered_memes(subreds, nsfw=None):
            subs = []
            for submission in await self.reddit.get_subreddits(subreds):
                if submission.url.endswith((".jpg", ".gif")) and not submission.is_self and submission.score >= 500:
                    if not nsfw or not submission.over_18 == nsfw:
                        subs.append(
                            self.reddit.sub_to_dict(
                                submission=submission,
                                permalink=True,
                                title=True,
                                url=True
                            )
                        )
            return subs

        async def update_memes():
            subs = await get_filtered_memes(memes_subs, nsfw=False)
            if subs != []:
                self.memes = subs
                utils.dump(subs, "cache/memes.json")

        async def update_nsfw_memes():
            subs = await get_filtered_memes(nsfw_memes_subs, nsfw=None)
            if subs != []:
                self.nsfw_memes = subs
                utils.dump(subs, "cache/nsfw_memes.json")

        start_time = time.time()
        tasks = [update_memes(), update_nsfw_memes()]
        await asyncio.gather(*tasks)
        await self.reddit.close()
        print(
            f"[+] Memes updated (took {(time.time() - start_time):.2f} sec for {len(memes_subs+nsfw_memes_subs)} subreddits). Submissions : {len(self.memes+self.nsfw_memes)}")

    @commands.command(name="avatar", aliases=["av"])
    @plugin_is_enabled()
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def show_avatar(self, ctx: commands.Context, member: discord.User = None):
        lang = self.client.fl(await self.client.get_lang(ctx.guild))
        text = lang.show_avatar

        member = member if member else ctx.author
        embed_text = text["embed"]
        embed = discord.Embed(
            description=embed_text["description"].format(
                member=member.mention),
            color=discord.Color.dark_gold()
        )
        embed.set_image(url=member.avatar)
        await ctx.reply(embed=embed)

    @commands.command(name="randomnumber", aliases=["randnum", "randint", "randnumber", "randomnum"])
    @plugin_is_enabled()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def get_random_number(self, ctx: commands.Context, x=None, y=None):
        try:
            x, y = int(x), int(y) if y else y
            if not y:
                y, x = x, 0
            await ctx.reply(f"{random.randint(x, y)} !")
        except:
            text = self.client.fl(await self.client.get_lang(ctx.guild)).get_random_number
            embed_text = text["checks"]["missing_args"]
            return await ctx.reply(
                embed=discord.Embed(
                    description="( ﾉ ﾟｰﾟ)ﾉ "+embed_text["description"],
                    color=discord.Color.dark_gold()
                )
            )

    @commands.command(name="twitter", aliases=["tw"])
    @plugin_is_enabled()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def ratio_twitter(self, ctx: commands.Context):
        """Twitter."""
        await ctx.message.delete()
        words = ["ratio", "nobody asked", "fatherless", "maidenless",
                 "no bitches", "don't care", "L", "ur bad", "poor",
                 "skill issue", "ew", "motherless", "orphan", "friendless",
                 "lifeless", "you're the reason your dad left", "cry about it", "stay mad", "adios"]
        random.shuffle(words)
        shuffled_words = words[0:random.randint(3, 5)]
        text = ""
        for word in shuffled_words:
            if word == shuffled_words[0]:
                text += word
            else:
                text += " + "+word
        if ctx.message.reference:
            reply_message = ctx.channel.get_partial_message(
                ctx.message.reference.message_id)
            await reply_message.reply(text, mention_author=False)
        else:
            await ctx.send(text)

    @staticmethod
    async def facto_image_viewer(ctx, lang, text, urls):
        def embed_generator(url):
            embed = discord.Embed(
                color=discord.Color.dark_gold()
            )
            embed.set_image(url=url)
            embed.set_footer(
                text=lang.DEFAULT_REQUESTED_FOOTER.format(author=ctx.author),
                icon_url=ctx.author.avatar if ctx.author.avatar else None
            )
            return embed

        random.shuffle(urls)

        button_text = text["buttons"]
        next_button = discord.ui.Button(
            style=discord.ButtonStyle.green,
            label=button_text["next"])
        previous_button = discord.ui.Button(
            style=discord.ButtonStyle.gray,
            label=button_text["previous"])

        image_viewer = EmbedViewer(
            ctx,
            urls,
            embed_generator,
            next_button,
            previous_button
        )

        await ctx.reply(
            embed=image_viewer.get_first_page(),
            view=image_viewer
        )

    @commands.command(name="shiba", aliases=["shibe", "shibb"])
    @plugin_is_enabled()
    @commands.has_permissions(attach_files=True)
    @commands.cooldown(1, 180, commands.BucketType.member)
    async def shibes_viewer(self, ctx: commands.Context):
        lang = self.client.fl(await self.client.get_lang(ctx.guild))
        text = lang.shibes_viewer
        await self.facto_image_viewer(ctx, lang, text, self.shibes)

    @commands.command(name="cat", aliases=["cats"])
    @plugin_is_enabled()
    @commands.has_permissions(attach_files=True)
    @commands.cooldown(1, 180, commands.BucketType.member)
    async def cats_viewer(self, ctx: commands.Context):
        lang = self.client.fl(await self.client.get_lang(ctx.guild))
        text = lang.cats_viewer
        await self.facto_image_viewer(ctx, lang, text, self.cats)

    @commands.command(name="bird", aliases=["birb", "birds"])
    @plugin_is_enabled()
    @commands.has_permissions(attach_files=True)
    @commands.cooldown(1, 180, commands.BucketType.member)
    async def birds_viewer(self, ctx: commands.Context):
        lang = self.client.fl(await self.client.get_lang(ctx.guild))
        text = lang.birds_viewer
        await self.facto_image_viewer(ctx, lang, text, self.birds)

    @staticmethod
    async def facto_meme_viewer(ctx, lang, text, dicts):
        def embed_generator(meme_dict):
            embed = discord.Embed(
                title=meme_dict["title"],
                url="https://reddit.com"+meme_dict["permalink"],
                color=discord.Color.dark_gold()
            )
            embed.set_image(url=meme_dict["url"])
            embed.set_footer(
                text=lang.DEFAULT_REQUESTED_FOOTER.format(author=ctx.author),
                icon_url=ctx.author.avatar if ctx.author.avatar else None
            )
            return embed

        random.shuffle(dicts)

        button_text = text["buttons"]
        next_button = discord.ui.Button(
            style=discord.ButtonStyle.green,
            label=button_text["next"])
        previous_button = discord.ui.Button(
            style=discord.ButtonStyle.gray,
            label=button_text["previous"])

        meme_viewer = EmbedViewer(
            ctx,
            dicts,
            embed_generator,
            next_button,
            previous_button
        )

        await ctx.reply(
            embed=meme_viewer.get_first_page(),
            view=meme_viewer
        )

    @commands.command(name="meme", aliases=["memes"])
    @plugin_is_enabled()
    @commands.has_permissions(attach_files=True)
    @commands.cooldown(1, 180, commands.BucketType.member)
    async def meme_viewer(self, ctx: commands.Context):
        lang = self.client.fl(await self.client.get_lang(ctx.guild))
        text = lang.meme_viewer
        await self.facto_meme_viewer(ctx, lang, text, self.memes)

    @commands.command(name="nsfwmeme", aliases=["nmeme", "nmemes"])
    @plugin_is_enabled()
    @utils.is_nsfw_or_dm()
    @commands.has_permissions(attach_files=True)
    @commands.cooldown(1, 180, commands.BucketType.member)
    async def nsfw_meme_viewer(self, ctx: commands.Context):
        lang = self.client.fl(await self.client.get_lang(ctx.guild))
        text = lang.nsfw_meme_viewer
        await self.facto_meme_viewer(ctx, lang, text, self.nsfw_memes)
