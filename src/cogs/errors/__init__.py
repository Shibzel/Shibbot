from .lang import English, French
from .cog import ErrorHandler


def setup(bot):
    bot.add_cog(ErrorHandler(bot))