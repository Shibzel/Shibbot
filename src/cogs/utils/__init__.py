from .lang import French, English
from .utilities import Utilities

def setup(bot):
    bot.add_cog(Utilities(bot))
