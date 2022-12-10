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

    pass