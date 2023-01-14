from .lang import French, English
from .entertainement import Fun


def setup(bot):
    bot.add_cog(Fun(bot))