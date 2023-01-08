import discord
from discord.ext import commands
import traceback

from src.core import Shibbot
from src.utils.logger import Logger
from src.constants import CACHE_PATH


logger = Logger(__name__)

def setup(bot):
    bot.add_cog(OwnerCommands(bot))

def create_log_file(error):
    path = CACHE_PATH+"/latest_error.log"
    with open(path, "w+") as f:
        f.write("".join(traceback.format_exception(type(error), error, error.__traceback__)))
    return path

class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: Shibbot = bot

    async def _on_cog(self, ctx, method, cog_name, method_name):
        try:   
            method(cog_name)
            await ctx.send(f"{method_name.title()}ed cog '{cog_name}' !")
        except Exception as error:
            message = f"Couldn't {method_name} '{cog_name}', the following error occured :"
            logger.error(message, error)
            await ctx.send(message, file=discord.File(fp=create_log_file(error)))

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, cog):
        await self._on_cog(ctx, self.bot.reload_extension, cog, "reload")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx: commands.Context, cog):
        await self._on_cog(ctx, self.bot.load_extension, cog, "load")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, cog):
        await self._on_cog(ctx, self.bot.unload_extension, cog, "unload")
