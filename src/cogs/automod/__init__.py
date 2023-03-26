from .automod import Automod


def setup(bot):
    bot.add_cog(Automod(bot))