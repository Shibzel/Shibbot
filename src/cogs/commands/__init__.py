from .lang import French, English
from .commands import BotsCommands


def setup(bot):
    bot.add_cog(BotsCommands(bot))