import discord
from discord.ext import commands

from bot import Shibbot


def setup(client):
    client.add_cog(BotEvents(client))


class BotEvents(commands.Cog):
    def __init__(self, client):
        self.client: Shibbot = client

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        """Makes the bot join the thread to listen to the thread's commands."""
        await thread.join()

    # @commands.Cog.listener()
    # async def on_guild_join(self, guild: discord.Guild):
    #     if guild.system_channel:
    #         channel = guild.system_channel
    #     elif guild.public_updates_channel:
    #         channel = guild.public_updates_channel
    #     else:
    #         for _channel in guild.channels:
    #             if isinstance(_channel, discord.TextChannel):
    #                 channel = _channel
    #                 break
    #         else:
    #             return

    #     prefix = self.client._get_prefix(guild)
    #     embed = discord.Embed(
    #         title="Wow !",
    #         color=discord.Color.dark_gold())
    #     embed.add_field(
    #         name="🇬🇧",
    #         value=f"Hemlo everyone, my name is **Shibbot**, thanks for inviting me on this server.\nTo get started use `{prefix}help` or `/help`, all my commands are here.",
    #         inline=False)
    #     embed.add_field(
    #         name="🇫🇷",
    #         value=f"Bonjour tout le monde, mon nom est **Shibbot**, merci de m'avoir invité.\nPar défaut à la première invitation du bot définit la langue par défaut en englais donc si cela est gênant utilisez la commande `{prefix}lang` afin de la changer, enfin pour accéder à la liste commandes faites `/help` ou `{prefix}help`.",
    #         inline=False)

    #     await channel.send(embed=embed)
