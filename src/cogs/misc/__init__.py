import discord
from discord.ext import bridge, commands

from src import Shibbot, BaseCog
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

    
    @bridge.bridge_command(name="avatar", aliases=["av"], description="Gives the profile picture.", description_localization={"fr": "Donne l'image de profil."},
                           options=[discord.Option(discord.User, name="user", name_localizations={"fr": "utilisateur"},
                                                   description="The user.", description_localizations={"fr": "L'utilisateur."})])
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
                           description_localizations={"fr": "Donne des infos sur un compte."}, options=[discord.Option(name="user", name_localizations={"fr": "utilisateur"},
                           description="The user.", description_localizations={"fr": "L'utilisateur."})])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def get_user_info(self, ctx: bridge.BridgeApplicationContext, user: discord.User = None):
        user = user if user else ctx.author