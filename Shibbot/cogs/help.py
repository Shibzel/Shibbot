from platform import python_version

import requests
import discord
from discord.ext import commands, bridge
import psutil

from bot import Shibbot, __version__


def setup(client):
    client.add_cog(Help(client))


class Help(commands.Cog):
    def __init__(self, client):
        self.client: Shibbot = client

        self.location = None
        try:
            result = requests.get(
                "http://ip-api.com/json/?fields=country,city")
            json_result = result.json()
            self.location = f"{json_result['city']}, {json_result['country']}"
        except:
            pass

    @commands.command(name="invite", aliases=["support", "botinvite"])
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def get_invitation(self, ctx: commands.Context):
        text = self.client.fl(await self.client.get_lang(ctx.guild)).get_invitation

        embed_text = text["embed"]
        embed = discord.Embed(
            title=embed_text["title"],
            description=embed_text["description"],
            color=discord.Color.dark_gold()
        )
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/955511076261347369/963461186756694096/happy_doggo.jpg")
        embed.set_footer(
            text=embed_text["footer"].format(
                version=self.client.version
            )
        )

        buttons_text = text["buttons"]
        invite_button = discord.ui.Button(
            label=buttons_text["bot_invite"],
            url=self.client.invite_bot_url
        )
        support_button = discord.ui.Button(
            label=buttons_text["support"],
            url=self.client.support_link
        )

        await ctx.reply(
            embed=embed,
            view=discord.ui.View(invite_button, support_button)
        )

    @commands.command(name="botinfo", aliases=["about"])
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def _bot_info(self, ctx: commands.Context):
        lang_code = await self.client.get_lang(ctx.guild)
        text = self.client.fl(lang_code).bot_info

        embed_text = text["embed"]
        embed = discord.Embed(color=discord.Color.dark_gold())
        embed.set_author(
            name=embed_text["title"],
            icon_url=self.client.user.avatar
        )
        fields_text = embed_text["fields"]
        embed.add_field(
            name=fields_text[0]["name"],
            value=fields_text[0]["value"].format(
                n_servers=len(self.client.guilds)
            )
        )
        embed.add_field(
            name=fields_text[1]["name"],
            value=fields_text[1]["value"].format(
                python_version=python_version(),
                pycord_version=discord.__version__,
                n_threads=psutil.cpu_count(logical=True),
                ram_usage=round(psutil.virtual_memory().used/1000000, 2),
                n_ram=round(psutil.virtual_memory().total/1000000, 2),
                place=self.location
            )
        )
        embed.add_field(
            name=fields_text[2]["name"],
            value=fields_text[2]["value"].format(
                donation_link="https://www.paypal.com/donate/?hosted_button_id=7WHDTVQR765B6"
            ),
            inline=False
        )
        await ctx.reply(embed=embed)

    @bridge.bridge_command(name="help", description="Stuck with the bot ? Use this command !")
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def show_help(self, ctx: bridge.BridgeContext):
        text = self.client.fl(await self.client.get_lang(ctx.guild)).show_help

        embed_text = text["embed"]
        embed = discord.Embed(
            title=embed_text["title"],
            description=embed_text["description"],
            color=discord.Color.dark_gold()
        )
        fields_text = embed_text["fields"]
        embed.add_field(
            name=fields_text[1]["name"],
            value=fields_text[1]["value"])
        embed.add_field(
            name=fields_text[0]["name"],
            value=fields_text[0]["value"])
        embed.add_field(
            name=fields_text[2]["name"],
            value=fields_text[2]["value"].format(prefix=await self.client._get_prefix(ctx)),
            inline=False
        )
        embed.set_thumbnail(url=self.client.user.avatar)
        embed.set_footer(text=embed_text["footer"].format(
            version=self.client.version))

        select_text = text["select"]
        select = discord.ui.Select(
            placeholder=select_text["placeholder"],
            options=[
                discord.SelectOption(
                    label=select_text["info"]["label"],
                    description=select_text["info"]["description"],
                    emoji="ℹ",
                    value="info"
                ),
                discord.SelectOption(
                    label=select_text["mod"]["label"],
                    description=select_text["mod"]["description"],
                    emoji="🔨",
                    value="mod"
                ),
                discord.SelectOption(
                    label=select_text["fun"]["label"],
                    description=select_text["fun"]["description"],
                    emoji="🎊",
                    value="fun"
                ),
                discord.SelectOption(
                    label=select_text["tools"]["label"],
                    description=select_text["tools"]["description"],
                    emoji="🔍",
                    value="tools"
                ),
            ])

        async def callback(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return

            embed._thumbnail = None
            embed_text = text[select.values[0]]
            embed.description = embed_text["description"]
            embed._fields = []
            for field in embed_text["fields"]:
                embed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=False
                )

            await interaction.response.edit_message(embed=embed)

        select.callback = callback

        buttons_text = text["buttons"]
        invite_button = discord.ui.Button(
            label=buttons_text["invite"],
            url=self.client.invite_bot_url)
        support_button = discord.ui.Button(
            label=buttons_text["support"],
            url=self.client.support_link)
        donate_button = discord.ui.Button(
            label=buttons_text["donate"],
            url="https://www.paypal.com/donate/?hosted_button_id=7WHDTVQR765B6")

        view = discord.ui.View(select, invite_button,
                               support_button, donate_button)

        if isinstance(ctx, (bridge.BridgeExtContext, commands.Context)):
            return await ctx.reply(embed=embed, view=view)
        elif isinstance(ctx, (bridge.BridgeApplicationContext, discord.ApplicationContext)):
            return await ctx.respond(embed=embed, view=view)
