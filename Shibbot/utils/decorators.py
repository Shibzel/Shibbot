import discord
from discord.ext import commands


def is_nsfw_or_dm():
    """Checks if we are in a dm channel, else if it's in a NSFW channel."""
    def predicate(ctx: commands.Context):
        channel = ctx.channel
        # If it's a NSFW channel or if it's in a dm channel
        if (ctx.guild and (isinstance(channel, discord.TextChannel) and channel.is_nsfw())) or not ctx.guild:
            return True
        raise commands.NSFWChannelRequired(channel)
    return commands.check(predicate)
