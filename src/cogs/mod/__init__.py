from .lang import English
from .moderation import Moderation
from .database import *

def setup(bot):
    bot.add_cog(Moderation(bot))