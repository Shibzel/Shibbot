from .lang import French, English
from .fun import Fun


def setup(bot):
    bot.add_cog(Fun(bot))