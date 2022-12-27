from .lang import English
from .cog import Moderation
from .database import *

def setup(bot):
    bot.add_cog(Moderation(bot))