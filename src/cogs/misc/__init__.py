from .lang import French, English
from .miscellaneous import Miscellaneous

def setup(bot):
    bot.add_cog(Miscellaneous(bot))
