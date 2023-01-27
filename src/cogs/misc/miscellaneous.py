import discord
from discord.ext import bridge, commands

from src.core import Shibbot
from src.utils import relative_timestamp, date_timestamp
from src.models.cog import BaseCog

from . import English, French


class Miscellaneous(BaseCog):
    def __init__(self, bot):
        self.bot: Shibbot = bot
        super().__init__(
            name={"en": "Miscellaneous", "fr": "Divers"},
            description={"en": "A variety of commands.", "fr": "Un ensemble de commandes variés."},
            languages={"en": English, "fr": French}, emoji="✨"
        )
    
    @bridge.bridge_command(name="avatar", aliases=["av"], description="Gives the profile picture.", description_localizations={"fr": "Donne l'image de profil."})
    @discord.option(name="user", name_localizations={"fr": "utilisateur"}, input_type=discord.User, required=False, 
                    description="The user whose profile picture you want.", description_localizations={"fr": "L'utilisateur dont vous souhaitez l'image de profil."})
    @commands.cooldown(3, 15, commands.BucketType.default)
    async def get_avatar(self, ctx: bridge.BridgeContext, user: discord.User = None):
        user = user if user else ctx.author
        lang = await self.get_lang(ctx)

        embed = discord.Embed(color=discord.Color.dark_gold())
        embed.set_footer(text=lang.DEFAULT_FOOTER.format(author=ctx.author), icon_url=ctx.author.avatar)
        embed.set_author(name=user)
        embed.set_image(url=user.avatar)
        await ctx.respond(embed=embed)

    @bridge.bridge_command(name="userinfo", aliases=["uinfo", "user-info"], description="Gives info about an account.",
                                                                            description_localizations={"fr": "Donne des infos sur un compte."})
    @discord.option(name="user", name_localizations={"fr": "utilisateur"}, input_type=discord.User,
                    description="The user you want more info about.", description_localizations={"fr": "L'utilisateur sur lequel voulez plus d'infos."})
    @commands.cooldown(1, 7, commands.BucketType.default)
    async def get_user_info(self, ctx: bridge.BridgeContext, user: discord.User = None):
        user = user if user else ctx.author
        lang = await self.get_lang(ctx)

        async with ctx.typing():
            if ctx.guild:
                potential_member = ctx.guild.get_member(user.id)
                if potential_member:
                    user: discord.Member = potential_member

            embed = discord.Embed(title=lang.GET_USER_INFO_TITLE, color=user.accent_color or discord.Color.dark_gold())
            if user.avatar:
                embed.set_thumbnail(url=user.avatar)
            embed.add_field(name=lang.GET_USER_INFO_FIELD1_NAME, value=lang.GET_USER_INFO_FIELD1_VALUE.format(user=user, user_id=user.id,
                                                                                                              date_creation_date=date_timestamp(user.created_at),
                                                                                                              relative_creation_date=relative_timestamp(user.created_at),
                                                                                                              is_bot='✔' if user.bot else '❌', common_serv=len(user.mutual_guilds)))
            if potential_member:
                status = {"online": "🟢", "dnd": "⛔", "idle": "🌙", "offline": "🔌"}
                embed.add_field(name=lang.GET_USER_INFO_FIELD2_NAME, value=lang.GET_USER_INFO_FIELD2_VALUE.format(nickname=user.display_name, 
                                                                                                                  joined_at=date_timestamp(user.joined_at), 
                                                                                                                  relative_joined_at=relative_timestamp(user.joined_at),
                                                                                                                  activity=user.activity.name if user.activity else 'N/A',
                                                                                                                  status=status[str(user.status)], top_role=user.top_role.mention))
            if user.banner:
                embed.set_image(url=user.banner.url)

        await ctx.respond(embed=embed)

    @bridge.bridge_command(name="serverinfo", aliases=["sinfo", "server-info"], description="Gives info about the server you're in.",
                                                                            description_localizations={"fr": "Donne des infos sur le serveur sur lequel vous êtes."})
    @bridge.guild_only()
    @commands.cooldown(1, 15, commands.BucketType.channel)
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def get_server_info(self, ctx: bridge.BridgeContext):
        lang = await self.get_lang(ctx)
        
        guild: discord.Guild = ctx.guild

        async with ctx.typing():
            embed = discord.Embed(title=lang.GET_SERVER_INFO_TITLE, description=lang.GET_SERVER_INFO_DESCRIPTION.format(guild=guild.name), color=discord.Color.dark_gold())
            if guild.icon:
                embed.set_thumbnail(url=guild.icon if guild.icon else None)

            embed.add_field(name=lang.GET_SERVER_INFO_FIELD1_NAME, value=lang.GET_SERVER_INFO_FIELD1_VALUE.format(guild_name=guild.name, guild_id=guild.id,
                                                                                                                  date_creation_date=date_timestamp(guild.created_at),
                                                                                                                  relative_creation_date=relative_timestamp(guild.created_at),
                                                                                                                  owner=guild.owner.mention,
                                                                                                                  owner_id=guild.owner.id,
                                                                                                                  premium_tier=guild.premium_tier,
                                                                                                                  premium_sub_tier=guild.premium_subscription_count,
                                                                                                                  bitrate=round(guild.bitrate_limit/1000)))

            members = guild.members
            member_count = len(members)
            bot_count = 0
            for member in members:
                if member.bot: bot_count += 1
            humain_count = member_count - bot_count    

            categories_count = len(guild.categories)
            channel_count = len(guild.channels) - categories_count
            text_count = len(guild.text_channels)
            forum_count = len(guild.forum_channels)
            voice_count = len(guild.voice_channels)
            stage_count = len(guild.stage_channels)

            embed.add_field(name=lang.GET_SERVER_INFO_FIELD2_NAME, value=lang.GET_SERVER_INFO_FIELD2_VALUE.format(
                                                                            member_count=member_count,
                                                                                humain_count=humain_count,
                                                                                    humain_count_percent=round(humain_count/member_count*100, 2),
                                                                                bot_count=bot_count,
                                                                                    bot_count_percent=round(bot_count/member_count*100, 2),
                                                                            channel_count=channel_count,
                                                                                categories_count=categories_count,
                                                                                text_count=text_count,
                                                                                    text_count_percent=round(text_count/channel_count*100, 2),
                                                                                forum_count=forum_count,
                                                                                    forum_count_percent=round(forum_count/channel_count*100, 2),
                                                                                voice_count=voice_count,
                                                                                    voice_count_percent=round(voice_count/channel_count*100, 2),
                                                                                stage_count=stage_count,
                                                                                    stage_count_percent=round(stage_count/channel_count*100, 2)))

            roles_str = ""
            roles = guild.roles
            roles.reverse()
            for role in roles:
                _roles_str = roles_str + role.mention + ("" if role == roles[-1] else ", ")
                if len(_roles_str) > 1024:
                    roles_str = "..."
                    break
                roles_str = _roles_str
            embed.add_field(name=lang.GET_SERVER_INFO_FIELD3_NAME, value=roles_str, inline=False)

            emojis_str = ""
            for emoji in guild.emojis:
                _emojis_str = emojis_str + f"<{'a' if emoji.animated else ''}:{emoji.name}:{emoji.id}> "
                if len(_emojis_str) > 1024:
                    emojis_str += "..."
                    break
                emojis_str = _emojis_str
            embed.add_field(name=lang.GET_SERVER_INFO_FIELD4_NAME, value=emojis_str if emojis_str != "" else lang.GET_SERVER_INFO_FIELD4_VALUE)

        await ctx.respond(embed=embed)

    @bridge.bridge_command(name="id", description="Get the id of an account.", description_localizations={"fr": "Obtiens l'id d'un compte."})
    @discord.option(name="user", name_localizations={"fr": "utilisateur"}, input_type=discord.User)
    @commands.cooldown(1, 5, commands.BucketType.default)
    async def _get_id(self, ctx: bridge.BridgeContext, user: discord.User = None):
        user = user or ctx.author
        await ctx.respond(content=f"{user}: `{user.id}`")