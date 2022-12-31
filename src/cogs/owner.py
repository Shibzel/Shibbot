import discord
from discord.ext import commands
import traceback

from src import Shibbot, COGS_PATH, Logger, CACHE_PATH, convert_to_import_path


cogs_path = convert_to_import_path(COGS_PATH)

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

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, cog):
        try:   
            self.bot.reload_extension(f"{cogs_path}.{cog}")
            await ctx.send(f"Reloaded cog {cog} !")
        except Exception as error:
            Logger.error(f"Couldn't reload '{cog}', the following error occured :", error)
            await ctx.send(f"Couldn't reload '{cog}', the following error occured :", file=discord.File(fp=create_log_file(error)))

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx: commands.Context, cog):
        try:
            self.bot.load_extension(f"{cogs_path}.{cog}")
            await ctx.send(f"Loaded cog {cog} !")
        except Exception as error:
            Logger.error(f"Couldn't load '{cog}', the following error occured :", error)
            await ctx.send(f"Couldn't load '{cog}', the following error occured :", file=discord.File(fp=create_log_file(error)))

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, cog):
        try:
            self.bot.unload_extension(f"{cogs_path}.{cog}")
            await ctx.send(f"Unloaded cog {cog} !")
        except Exception as error:
            Logger.error(f"Couldn't unload '{cog}', the following error occured :", error)
            await ctx.send(f"Couldn't unload '{cog}', the following error occured :", file=discord.File(fp=create_log_file(error)))