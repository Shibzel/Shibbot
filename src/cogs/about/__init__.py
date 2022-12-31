from .lang import French, English
from .about import About


def setup(bot):
    bot.add_cog(About(bot))