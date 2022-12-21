from .lang import French, English
from .cog import Miscellaneous

def setup(bot):
    bot.add_cog(Miscellaneous(bot))
