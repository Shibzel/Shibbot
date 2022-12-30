import threading
import gc

from .utils import Logger, Uptime
from .constants import COGS_PATH

path = COGS_PATH
if path.startswith("./"):
    path = path[2:]
path = path.replace('/', '.')


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

    
    def apply_on_cog(self, method, method_name, cog_name):
        try:
            method(f"{path}.{cog_name}")
            Logger.log(f"Successfully {method_name}ed '{cog_name}' cog.")
        except Exception as e:
            Logger.error(f"Could not {method_name} '{cog_name}' cog.", e)


    @command
    def stop(self, *args):
        try: raise ConsoleInterruption
        except ConsoleInterruption as e: self.bot.loop.create_task(self.bot.close(e))
        self.kill()

    
    @command
    def gc(self, *args):
        gc.collect()
        Logger.log("Done running GC !")


    @command
    def load(self, cog, *args):
        self.apply_on_cog(self.bot.load_extension, "load", cog)


    @command
    def unload(self, cog, *args):
        self.apply_on_cog(self.bot.unload_extension, "unload", cog)

    
    @command
    def reload(self, cog, *args):
        self.apply_on_cog(self.bot.reload_extension, "reload", cog)

    
    @command
    def uptime(self, *args):
        uptime = Uptime(self.bot.init_time)
        Logger.log(f"Up for : {uptime.days} days, {uptime.hours} hours, {uptime.minutes} min and {uptime.seconds} sec.")


    def main(self):
        Logger.log(f"Using command inputs ({', '.join(commands.keys())}).")

        while self.running:
            raw_command = input()
            list_command = raw_command.split(" ")
            command_name, command_args = list_command[0], list_command[1:]
            Logger.log(f"Console : '{raw_command}'")
            if commands.get(command_name):
                try:
                    commands[command_name](self, *command_args)
                except TypeError as e:
                    Logger.error(f"Missing arguments.", e)
            else:
                Logger.log(f"Unknown command '{command_name}'.")

    def start(self):
        self.thread.start()   

    def kill(self):
        self.running = False