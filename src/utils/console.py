import threading
import gc

from .logger import Logger
from .hardware import Uptime


logger = Logger(__name__)

class ConsoleInterruption(Exception):
    def __init__(self, message=None):
        super().__init__(message or "Shibbot was asked to stop by the console.")

commands = {}
def command(foo):
        commands[foo.__name__] = foo
        return foo

class ConsoleThread:
    def __init__(self, bot):
        self.bot = bot
        self.running = True

        self.thread = threading.Thread(target=self.main, name="ConsoleThread")

    @staticmethod
    def strinify_command(command_name):
        _command = commands[command_name]
        return f"{command_name}: {_command.__doc__ if _command.__doc__ else 'No description provided.'}"

    @command
    def help(self, command_name: str | None = None, *args):
        """Shows all console commands. Args: 'command_name' (optional)."""
        if not command_name:
            logger.log("Available commands :\n"+"\n".join([self.strinify_command(name) for name in commands.keys()]))
        elif commands.get(command_name):
            logger.log(self.strinify_command(command_name))
        else:
            logger.error(f"Unknown command '{command_name}'. Try 'help' again but without arguments to see te full list of console commands.")
    
    @command
    def cogs(self, *args):
        """Shows all the enabled cogs."""
        logger.log("Enabled cogs :\n[\n    {0}\n]".format(',\n    '.join(self.bot.cogs.keys())))

    @staticmethod
    def apply_on_cog(method, method_name, cog_name):
        try:
            method(cog_name)
            logger.log(f"Successfully {method_name}ed '{cog_name}' cog.")
        except Exception as e:
            logger.error(f"Could not {method_name} '{cog_name}' cog.", e)
    
    @command
    def load(self, cog_name, *args):
        """Loads a cog. Args: 'cog_name' (needed)."""
        self.apply_on_cog(self.bot.load_extension, "load", cog_name)

    @command
    def unload(self, cog_name, *args):
        """Unloads a cog. Args: 'cog_name' (needed)."""
        self.apply_on_cog(self.bot.unload_extension, "unload", cog_name)

    @command
    def reload(self, cog_name, *args):
        """Reloads a cog. Args: 'cog_name' (needed)."""
        self.apply_on_cog(self.bot.reload_extension, "reload", cog_name)

    @command
    def gc(self, *args):
        """Runs the garbage collector."""
        gc.collect()
        logger.log("Done running GC !")

    @command
    def uptime(self, *args):
        """Shows the uptime."""
        uptime = Uptime(self.bot.init_time)
        logger.log(f"Up for : {uptime.days} days, {uptime.hours} hours, {uptime.minutes} min and {uptime.seconds} sec.")

    @command
    def servers(self, *args):
        """Shows the numbers of guilds."""
        logger.log(f"This instance is currently on {len(self.bot.guilds)} servers.")
    
    @command
    def users(self, *args):
        """Shows the numbers of users."""
        logger.log(f"This instance is watching over {len(self.bot.users)} users.")

    @command
    def stop(self, *args):
        """Stops the bot."""
        logger.log("Stopping Shibbot...")
        try: raise ConsoleInterruption
        except ConsoleInterruption as e: self.bot.loop.create_task(self.bot.close(e))
        self.kill()

    def main(self):
        logger.log(f"Console commands available ({', '.join(commands.keys())}).")

        while self.running:
            raw_command = input()
            list_command = raw_command.split(" ")
            command_name, command_args = list_command[0], list_command[1:]
            logger.log(f"Console : '{raw_command}'")
            if commands.get(command_name):
                try:
                    commands[command_name](self, *command_args)
                except TypeError as e:
                    logger.error(f"Missing arguments.", e)
            else:
                logger.error(f"Unknown command '{command_name}'. Try 'help' to see te full list of console commands.")

    def start(self):
        self.thread.start()  

    def kill(self):
        self.running = False