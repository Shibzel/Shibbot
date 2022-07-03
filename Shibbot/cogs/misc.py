import discord
from discord.ext import commands

from bot import Shibbot
from utils import date_timestamp, relative_timestamp


def setup(client):
    client.add_cog(Misc(client))


class Misc(commands.Cog):
    def __init__(self, client):
        self.client: Shibbot = client

    @commands.command(name="avatar", aliases=["av"])
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
        embed.set_footer(
            text=lang.DEFAULT_REQUESTED_FOOTER.format(author=ctx.author),
            icon_url=ctx.author.avatar if ctx.author.avatar else None
        )
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.reply(embed=embed)

    @commands.command(name="serverinfo", aliases=["guildinfo", "sinfo", "ginfo"])
    @commands.guild_only()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def get_guild_info(self, ctx: commands.Context):
        """Gives information about the guild."""
        lang = self.client.fl(await self.client.get_lang(ctx.guild))
        text = lang.get_guild_info

        async with ctx.typing():
            guild: discord.Guild = ctx.guild
            embed_text = text["loading_embed"]
            embed = discord.Embed(
                description="⌛ "+embed_text["description"],
                color=discord.Color.dark_gold()
            )
            message = await ctx.reply(embed=embed)

            embed_text = text["embed"]
            embed.title = embed_text["title"]
            embed.description = embed_text["description"].format(
                guild=guild.name)
            if guild.icon:
                embed.set_thumbnail(url=guild.icon if guild.icon else None)
            fields_text = embed_text["fields"]
            embed.add_field(
                name=fields_text[0]["name"],
                value=fields_text[0]["value"].format(
                    guild_name=guild.name,
                    guild_id=guild.id,
                    date_creation_date=date_timestamp(guild.created_at),
                    relative_creation_date=relative_timestamp(
                        guild.created_at),
                    owner=guild.owner.mention,
                    owner_id=guild.owner.id,
                    premium_tier=guild.premium_tier,
                    premium_sub_tier=guild.premium_subscription_count,
                    verification_level=guild.verification_level
                )
            )

            members = guild.members
            member_count, humain_count, bot_count = len(members), 0, 0
            for member in members:
                if member.bot:
                    bot_count += 1
                else:
                    humain_count += 1
            channels = guild.channels
            channel_count, category_count, text_count, voice_count = 0, 0, 0, 0
            for channel in channels:
                if isinstance(channel, discord.TextChannel):
                    text_count += 1
                    channel_count += 1
                elif isinstance(channel, (discord.VoiceChannel, discord.StageChannel)):
                    voice_count += 1
                    channel_count += 1
                elif isinstance(channel, discord.CategoryChannel):
                    category_count += 1
            embed.add_field(
                name=fields_text[1]["name"],
                value=fields_text[1]["value"].format(
                    member_count=member_count,
                    humain_count=humain_count,
                    humain_count_percent=round(
                        humain_count/member_count*100, 2),
                    bot_count=bot_count,
                    bot_count_percent=round(bot_count/member_count*100, 2),
                    channel_count=channel_count,
                    category_count=category_count,
                    text_count=text_count,
                    text_count_percent=round(text_count/channel_count*100, 2),
                    voice_count=voice_count,
                    voice_count_percent=round(voice_count/channel_count*100, 2)
                )
            )

            roles_str = ""
            roles = guild.roles
            roles.reverse()
            for role in roles:
                _roles_str = roles_str + f"`{role}`" + \
                    ("" if role == roles[-1] else ", ")
                if len(_roles_str) > 1024:
                    roles_str = "..."
                    break
                roles_str = _roles_str
            embed.add_field(
                name=fields_text[2]["name"],
                value=roles_str,
                inline=False
            )

            emojis_str = ""
            for emoji in guild.emojis:
                _emojis_str = emojis_str + \
                    f"<{'a' if emoji.animated else ''}:{emoji.name}:{emoji.id}> "
                if len(_emojis_str) > 1024:
                    emojis_str += "..."
                    break
                emojis_str = _emojis_str
            embed.add_field(
                name=fields_text[3]["name"],
                value=emojis_str if emojis_str != "" else fields_text[3]["value"]
            )

        return await message.edit(embed=embed)

    @commands.command(name="userinfo", aliases=["memberinfo", "uinfo"])
    @commands.guild_only()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def get_user_info(self, ctx: commands.Context, user: discord.User = None):
        """Gives information about the mentioned user."""
        lang = self.client.fl(await self.client.get_lang(ctx.guild))
        text = lang.get_user_info

        async with ctx.typing():
            if not user:
                user = ctx.author
            if ctx.guild:
                potential_member = ctx.guild.get_member(user.id)
                if potential_member:
                    user: discord.Member = potential_member

            embed_text = text["loading_embed"]
            embed = discord.Embed(
                description="⌛ "+embed_text["description"],
                color=discord.Color.dark_gold()
            )
            message = await ctx.reply(
                embed=embed
            )

            embed_text = text["embed"]
            embed.title = embed_text["title"]
            embed.description = None
            if user.avatar:
                embed.set_thumbnail(url=user.avatar)
            fields_text = embed_text["fields"]
            embed.add_field(
                name=fields_text[0]["name"],
                value=fields_text[0]["value"].format(
                    user=user,
                    user_id=user.id,
                    date_creation_date=date_timestamp(user.created_at),
                    relative_creation_date=relative_timestamp(
                        user.created_at),
                    is_bot='✔' if user.bot else '❌',
                    common_serv=len(user.mutual_guilds)
                )
            )
            if potential_member:
                embed.add_field(
                    name=fields_text[1]["name"],
                    value=fields_text[1]["value"].format(
                        nickname=user.display_name,
                        joined_at=date_timestamp(user.joined_at),
                        relative_joined_at=relative_timestamp(user.joined_at),
                        activity=user.activity.name if user.activity else 'none',
                        status=user.status,
                        top_role=user.top_role.mention
                    )
                )
            if user.banner:
                embed.set_image(url=user.banner.url)
        return await message.edit(embed=embed)
