import threading
import gc

from .utils import Logger
from .constants import COGS_PATH

path = COGS_PATH
if path.startswith("./"):
    path = path[2:]
path = path.replace('/', '.')


class ConsoleInterruption(Exception):
    def __init__(self, message=None):
        super().__init__(message or "Shibbot was asked to stop by the console.")

class ConsoleThread(threading.Thread):
    def __init__(self, bot):
        super().__init__(target=self.terminal_command, args=(bot,), name="ConsoleThread")

    def terminal_command(self, bot):
        Logger.log(f"Using command inputs (gc, stop).")
        def on_cog(method, method_name):
            cog_name = command.replace(method_name, "")
            try:
                method(f"{path}.{cog_name}")
                Logger.log(f"Successfully {method_name}'{cog_name}' cog.")
            except Exception as e:
                Logger.error(f"Could not {method_name}'{cog_name}' cog.", e)

        while True:
            command = input()
            Logger.log(f"Console : '{command}'")

            if command.startswith("load "):
                on_cog(bot.load_extension, "load ")
            elif command.startswith("unload "):
                on_cog(bot.unload_extension, "unload ")
            elif command.startswith("reload "):
                on_cog(bot.unload_extension, "reload ")
            else:
                match command:
                    case "stop":
                        try: raise ConsoleInterruption
                        except ConsoleInterruption as e: bot.loop.create_task(bot.close(e))
                        return
                    case "gc":
                        gc.collect()
                        Logger.log("Done running GC !")
                    case _:
                        Logger.log("Unknown command.")