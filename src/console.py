"""Everything about the terminal and the actions that can be taken with it."""
import gc
import json
from threading import Thread

from .logging import Logger


logger = Logger(__name__)

class ConsoleInterruption(Exception):
    """Raised when the bot is stopping because of an user interaction."""
    def __init__(self, message=None):
        super().__init__(message or "Shibbot was asked to stop by the console.")

commands = {}
without_aliases = []
def command(name: str = None, aliases: list = None):
    """A decorator indicating that this function is a console command."""
    def pred(foo):
        nonlocal name
        name = name or foo.__name__
        without_aliases.append(name)
        for n in [name, *aliases] if aliases else [name]:
            commands[n] = foo
        return foo
    return pred

class Console:
    """Console object for Shibbot.
    
    Attributes:
    ----------
    bot: Shibbot
        The instance of Shibbot.
    running: bool
        Watever the input loop is running or not.
    thread: threading.Thread
        The thread object.
    """
    def __init__(self, bot):
        """Parameters:
        ----------
        bot: Shibbot
            The instance of Shibbot."""
        self.bot = bot
        self.running = True

        self.thread = Thread(target=self.main, name="ConsoleThread")
             
    def main(self):
        """The code running inside the thread."""
        logger.log("Console commands available. Type 'help'.")

        while self.running:
            raw_command = input()
            if raw_command == "":
                continue
            
            list_command = raw_command.split(" ")
            command_name, command_args = list_command[0], list_command[1:]
            logger.log(f"Console input : '{raw_command}'")
            
            if commands.get(command_name):
                try:
                    commands[command_name](self, *command_args)
                except ConsoleInterruption as e:
                    raise e
                except TypeError as e:
                    logger.error(f"Missing arguments.", e)
                except Exception:
                    logger.error("Something went wrong in the console.", e)
            else:
                logger.error(f"Unknown command '{command_name}'. Try 'help' to see te full list of console commands.")

    def start(self) -> None:
        """Starts the input thread."""
        self.thread.start()

    @staticmethod
    def strinify_command(command_name):
        _command = commands[command_name]
        return f"{command_name}: {_command.__doc__ if _command.__doc__ else 'No description provided.'}"

    @command()
    def help(self, command_name: str | None = None, *args):
        """Shows all console commands. Args: 'command_name' (optional)."""
        if not command_name:
            logger.log(f"Available commands : {', '.join(without_aliases)}.")
        elif commands.get(command_name):
            logger.log(self.strinify_command(command_name))
        else:
            logger.error(f"Unknown command '{command_name}'. Try 'help' again but without arguments to see te full list of console commands.")
        
    @command()
    def ping(self, *args):
        """Returns the ping of the bot."""
        logger.log(f"Ping: {round(self.bot.latency*1000, 2)}ms.")

    @command()
    def uptime(self, *args):
        """Shows the uptime."""
        uptime = self.bot.uptime
        logger.log(f"Up for : {uptime.days} days, {uptime.hours} hours, {uptime.minutes} min and {uptime.seconds} sec.")

    @command()
    def stats(self, *args):
        """Shows some stats."""
        ut = self.bot.uptime
        logger.log(f"Statistics :\nPing: {round(self.bot.latency*1000, 2)}ms\nUptime : {ut.days}d {ut.hours}h {ut.minutes}m {ut.seconds}s\nInvoked commands : {self.bot.invoked_commands}\n" + \
            f"Average processing time : {self.bot.avg_processing_time:.2f}ms\nBiggest server : {max(len(guild.members) for guild in self.bot.guilds)} members")        

    @command()
    def cogs(self, *args):
        """Shows all the enabled cogs."""
        logger.log(f"Enabled cogs :\n{json.dumps({name: repr(cog) for name, cog in self.bot.cogs.items()}, indent=4)}")

    @staticmethod
    def _apply_on_cog(method, method_name, cog_name):
        try:
            method(cog_name)
            logger.log(f"Successfully {method_name}ed '{cog_name}' cog.")
        except Exception as e:
            logger.error(f"Could not {method_name} '{cog_name}' cog.", e)
    
    @command()
    def load(self, cog_name, *args):
        """Loads a cog. Args: 'cog_name' (needed)."""
        self._apply_on_cog(self.bot.load_extension, "load", cog_name)

    @command()
    def unload(self, cog_name, *args):
        """Unloads a cog. Args: 'cog_name' (needed)."""
        self._apply_on_cog(self.bot.unload_extension, "unload", cog_name)

    @command()
    def reload(self, cog_name, *args):
        """Reloads a cog. Args: 'cog_name' (needed)."""
        self._apply_on_cog(self.bot.reload_extension, "reload", cog_name)

    @command()
    def gc(self, *args):
        """Runs the garbage collector."""
        gc.collect()
        logger.log("Done running GC !")
        
    @command()
    def debug(self, enabled: str = None, *args):
        if not enabled:
            logger.log(f"Debug for logging is set as '{logger.is_enabled()}'. Type 'debug true/false' to enable or disable it.")
        else:
            enabled = enabled.lower() == "true"
            self.bot.set_debug(enabled)
            if enabled:
                logger.log(f"Setting debug mode for logging as '{enabled}'.")

    @command(aliases=["close"])
    def stop(self, *args):
        """Stops the bot."""
        logger.log("Are you sure ? (Y/N) :")
        response = input()
        if response.lower() in ("y", ""):
            self.forcestop()
        else:
            logger.log("Aborted.")

    @command(aliases=["adios"])
    def forcestop(self, *args):
        """Stops the bot without asking if the user is sure."""
        logger.log("Stopping Shibbot...")
        self.bot.loop.create_task(self.bot.close(ConsoleInterruption()))
        self.running = False