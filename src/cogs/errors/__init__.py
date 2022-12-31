from .lang import English, French
from .errorHandler import ErrorHandler


def setup(bot):
    bot.add_cog(ErrorHandler(bot))