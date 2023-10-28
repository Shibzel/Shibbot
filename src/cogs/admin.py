import discord
from discord.ext import commands
import traceback

from src.core import Shibbot
from src.models.cog import BaseCog

def setup(bot):
    bot.add_cog(OwnerCommands(bot))

def create_log_file(bot, error):
    path = bot.temp_cache_path+"/latest_error.log"
    with open(path, "w+") as f:
        f.write("".join(traceback.format_exception(type(error), error, error.__traceback__)))
    return path

class OwnerCommands(BaseCog):
    def __init__(self, bot: Shibbot):
        self.bot = bot
        super().__init__(hidden=True)

    async def _on_cog(self, ctx, method, cog_name, method_name):
        try:   
            method(cog_name)
            await ctx.send(f"{method_name.title()}ed cog `{cog_name}` !")
        except Exception as error:
            message = f"Couldn't {method_name} '{cog_name}', the following error occured :"
            self.logger.error(message, error)
            await ctx.send(message, file=discord.File(fp=create_log_file(self.bot, error)))

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
        
    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context):
        try:   
            await self.bot.sync_commands()
            await ctx.send("Synced all commands !")
        except Exception as error:
            message = "Couldn't sync commands."
            self.logger.error(message, error)
            await ctx.send(message, file=discord.File(fp=create_log_file(self.bot, error)))
        
    @commands.command()
    async def owner(self, ctx: commands.Context):
        if ctx.author == self.bot.project_owner:
            await ctx.send(f"Hey {self.bot.project_owner.mention}, I know you ! You wrote my code !")
            
    @commands.command()
    @commands.is_owner()
    async def latestlogs(self, ctx: commands.Context):
        await ctx.send(file=discord.File(fp=self.logger.file))