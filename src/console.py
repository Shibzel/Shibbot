import threading
import gc

from .logging import Logger


logger = Logger(__name__)

class ConsoleInterruption(Exception):
    def __init__(self, message=None):
        super().__init__(message or "Shibbot was asked to stop by the console.")

commands = {}
def command(name: str = None, aliases: list = None):
    def pred(foo):
        nonlocal name
        name = name or foo.__name__
        names = [name, *aliases] if aliases else [name]
        for name in names:
            commands[name] = foo
        return foo
    return pred

class Console:
    def __init__(self, bot):
        self.bot = bot
        self.running = True

        self.thread = threading.Thread(target=self.main, name="ConsoleThread")

    @staticmethod
    def strinify_command(command_name):
        _command = commands[command_name]
        return f"{command_name}: {_command.__doc__ if _command.__doc__ else 'No description provided.'}"

    @command()
    def help(self, command_name: str | None = None, *args):
        """Shows all console commands. Args: 'command_name' (optional)."""
        if not command_name:
            logger.log(f"Available commands : {', '.join(commands)}.")
        elif commands.get(command_name):
            logger.log(self.strinify_command(command_name))
        else:
            logger.error(f"Unknown command '{command_name}'. Try 'help' again but without arguments to see te full list of console commands.")
            
    @command()
    def ping(self, *args):
        """Returns the ping of the bot."""
        logger.log(f"Ping: {round(self.bot.latency*1000, 2)}ms.")
    
    @command()
    def cogs(self, *args):
        """Shows all the enabled cogs."""
        logger.log("Enabled cogs :\n[\n    {0}\n]".format(',\n    '.join(self.bot.cogs)))

    @staticmethod
    def apply_on_cog(method, method_name, cog_name):
        try:
            method(cog_name)
            logger.log(f"Successfully {method_name}ed '{cog_name}' cog.")
        except Exception as e:
            logger.error(f"Could not {method_name} '{cog_name}' cog.", e)
    
    @command()
    def load(self, cog_name, *args):
        """Loads a cog. Args: 'cog_name' (needed)."""
        self.apply_on_cog(self.bot.load_extension, "load", cog_name)

    @command()
    def unload(self, cog_name, *args):
        """Unloads a cog. Args: 'cog_name' (needed)."""
        self.apply_on_cog(self.bot.unload_extension, "unload", cog_name)

    @command()
    def reload(self, cog_name, *args):
        """Reloads a cog. Args: 'cog_name' (needed)."""
        self.apply_on_cog(self.bot.reload_extension, "reload", cog_name)

    @command()
    def gc(self, *args):
        """Runs the garbage collector."""
        gc.collect()
        logger.log("Done running GC !")

    @command()
    def uptime(self, *args):
        """Shows the uptime."""
        uptime = self.bot.uptime
        logger.log(f"Up for : {uptime.days} days, {uptime.hours} hours, {uptime.minutes} min and {uptime.seconds} sec.")

    @command()
    def stats(self, *args):
        """Shows some stats."""
        ut = self.bot.uptime
        logger.log(f"Statistics :\nUptime : {ut.days}d {ut.hours}h {ut.minutes}m {ut.seconds}s\nInvoked commands : {self.bot.invoked_commands}\nAverage processing time : {self.bot.avg_processing_time:.4f}ms\nBiggest server : {max(len(guild.members) for guild in self.bot.guilds)} members")        

    @command(aliases=["close"])
    def stop(self, *args):
        """Stops the bot."""
        response = input("Are you sure ? (Y/N)")
        if response.lower() in ("y", ""):
            self.adios()
        else:
            logger.log("Aborted.")

    @command(aliases=["forcestop"])
    def adios(self, *args):
        """Stops the bot without asking if the user is sure."""
        logger.log("Stopping Shibbot...")
        self.bot.loop.create_task(self.bot.close(ConsoleInterruption()))
        self.running = False
        
    def main(self):
        logger.log("Console commands available. Type 'help'.")

        while self.running:
            raw_command = input()
            if raw_command == "": continue
            list_command = raw_command.split(" ")
            command_name, command_args = list_command[0], list_command[1:]
            logger.log(f"Console : '{raw_command}'")
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

    def start(self):
        self.thread.start()