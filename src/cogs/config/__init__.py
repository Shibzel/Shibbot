from .lang import French, English
from .cog import Configuration


def setup(bot):
    bot.add_cog(Configuration(bot))