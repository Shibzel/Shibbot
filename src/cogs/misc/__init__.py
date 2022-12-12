import discord
from discord.ext import bridge, commands

from src import Shibbot, BaseCog, relative_timestamp, date_timestamp
from .lang.en import English
from .lang.fr import French


def setup(bot):
    bot.add_cog(MiscCog(bot))


class MiscCog(BaseCog):
    
    def __init__(self, bot):
        self.bot: Shibbot = bot
        super().__init__(
            bot=bot,
            name={"en": "Miscellaneous", "fr": "Divers"},
            description={"en": "A variety of commands.", "fr": "Un ensemble de commandes variés."},
            languages = {"en": English, "fr": French}, emoji="✨"
        )

    
    @bridge.bridge_command(name="avatar", aliases=["av"], description="Gives the profile picture.", description_localizations={"fr": "Donne l'image de profil."})
    @discord.option(name="user", name_localizations={"fr": "utilisateur"}, input_type=discord.User, required=False, 
                    description="The user whose profile picture you want.", description_localizations={"fr": "L'utilisateur dont vous souhaitez l'image de profil."})
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def get_avatar(self, ctx: bridge.BridgeApplicationContext, user: discord.User = None):
        user = user if user else ctx.author
        lang = await self.get_lang(ctx)

        embed = discord.Embed(color=discord.Color.dark_gold())
        embed.set_footer(text=lang.DEFAULT_FOOTER.format(author=ctx.author), icon_url=ctx.author.avatar)
        embed.set_author(name=user)
        embed.set_image(url=user.avatar)
        await ctx.respond(embed=embed)


    @bridge.bridge_command(name="user-info", aliases=["uinfo", "userinfo"], description="Gives info about an account.",
                                                                            description_localizations={"fr": "Donne des infos sur un compte."})
    @discord.option(name="user", name_localizations={"fr": "utilisateur"}, input_type=discord.User, required=False, 
                    description="The user you want more info about.", description_localizations={"fr": "L'utilisateur sur lequel voulez plus d'infos."})
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def get_user_info(self, ctx: bridge.BridgeApplicationContext, user: discord.User = None):
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