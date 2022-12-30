from .lang import French, English
from .cog import About


def setup(bot):
    bot.add_cog(About(bot))