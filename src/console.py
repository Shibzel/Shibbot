import gc
import asyncio
from threading import Thread
from sqlite3 import ProgrammingError

from . import __version__
from .logging import LoggingLevel, SubLogger


__all__ = ("ConsoleInterruption", "Console")


class ConsoleInterruption(Exception):
    """Raised when the bot is stopping because of an user interaction."""

    def __init__(self, message=None):
        super().__init__(message or "Shibbot was asked to stop by the console.")

_commands = {}
_without_aliases = []

def console_command(name: str = None, aliases: list = None):
    """A decorator indicating that a function is a console command."""
    def command(foo):
        nonlocal name
        name = name or foo.__name__
        _without_aliases.append(name)
        for n in [name, *aliases] if aliases else [name]:
            _commands[n] = foo
        return foo
    return command

class Console(Thread):
    """Console object for Shibbot."""

    def __init__(self, bot):
        self.bot = bot
        self.logger: SubLogger = bot.logger.get_logger(__name__)
        self.running = True
        super().__init__(target=self.__main__, name="ConsoleThread")

    def __main__(self) -> None:
        """The code running inside the thread."""
        self.logger.log("Console enabled. Type 'help'.")

        while self.running:
            raw_command = input()
            if raw_command == "":
                continue
            list_command = raw_command.split(" ")
            command_name, command_args = list_command[0], list_command[1:]

            if _commands.get(command_name):
                try:
                    _commands[command_name](self, *command_args)
                except TypeError:
                    comm_help = self.strinify_console_command(command_name)
                    self.logger.log(comm_help)
                except ConsoleInterruption as err:
                    raise err
                except Exception as err:
                    self.logger.error("Something went wrong in the console.", err)
            else:
                self.logger.error(f"Unknown command '{command_name}'."
                             " Try 'help' to see te full list of console commands.")

    def strinify_console_command(self, command_name) -> str:
        _command = _commands[command_name]
        description = _command.__doc__ if _command.__doc__ else 'No description provided.'
        return f"{command_name}: {description}"

    @console_command()
    def help(self, command_name: str | None = None, *args):
        """Shows all console commands. Args: 'command_name' (optional)."""
        if not command_name:
            self.logger.log(f"Available commands : {', '.join(_without_aliases)}.")
        elif _commands.get(command_name):
            self.logger.log(self.strinify_console_command(command_name))
        else:
            self.logger.error(f"Unknown command '{command_name}'."
                         " Try 'help' again but without arguments to see the"
                         " full list of console commands.")

    @console_command()
    def ping(self, *args):
        """Returns the ping of the bot."""
        self.logger.log(f"Ping: {round(self.bot.latency*1000, 2)}ms.")

    @console_command()
    def uptime(self, *args):
        """Shows the uptime."""
        uptime = self.bot.uptime
        self.logger.log(f"Up for : {uptime.days} days, {uptime.hours} hours,"
                   f" {uptime.minutes} min and {uptime.seconds} sec.")

    @console_command()
    def stats(self, *args):
        """Shows some stats."""
        ut = self.bot.uptime
        self.logger.log("Statistics :\n"
            f"Version of Shibbot : v{__version__}\n"
            f"Cogs: {len(self.bot.cogs)} ({len(self.bot.plugins)} plugins)\n"
            f"Ping: {round(self.bot.latency*1000, 2)}ms\n"
            f"Uptime : {ut.days}d {ut.hours}h {ut.minutes}m {ut.seconds}s\n"
            f"Users : {len(self.bot.users)}\n"
            f"Guilds : {len(self.bot.guilds)}\n"
            f"Biggest server : {max(len(guild.members) for guild in self.bot.guilds)} members\n"
            f"Invoked commands : {self.bot.invoked_commands}\n"
            f"Average processing time : {self.bot.avg_processing_time:.2f}ms"
        )

    @console_command()
    def cogs(self, *args):
        """Shows all the enabled cogs."""
        cogs: dict = self.bot.cogs
        text = f"Enabled cogs ({len(cogs)}) :\n"
        for k, cog in cogs.items():
            cog_type = type(cog)
            bases = ", ".join(base.__name__ for base in cog_type.__bases__)
            text += f"'{k}' ({bases}) located at '{cog_type.__module__}'."  # What the fuck is that ?
            if author:= getattr(cog, "author", None):
                text += f" Author: {author}."
            if k != list(cogs.keys())[-1]:
                text += f"\n"
        self.logger.log(text)

    def _apply_on_cog(self, method, method_name, cog_name) -> None:
        async def task():
            try:
                method(cog_name)
                self.logger.log(f"Successfully {method_name}ed '{cog_name}' cog.")
            except ProgrammingError as exc:
                raise exc
            except Exception as err:
                self.logger.error(f"Could not {method_name} '{cog_name}' cog.", err)
        self.logger.log("The action on this cog is planned, it can take some time if the bot is busy.")
        self.bot.loop.call_soon(asyncio.ensure_future, task())

    @console_command()
    def load(self, cog_name, *args):
        """Loads a cog. Args: 'cog_name' (needed)."""
        self._apply_on_cog(self.bot.load_extension, "load", cog_name)

    @console_command()
    def unload(self, cog_name, *args):
        """Unloads a cog. Args: 'cog_name' (needed)."""
        self._apply_on_cog(self.bot.unload_extension, "unload", cog_name)

    @console_command()
    def reload(self, cog_name, *args):
        """Reloads a cog. Args: 'cog_name' (needed)."""
        self._apply_on_cog(self.bot.reload_extension, "reload", cog_name)

    @console_command()
    def gc(self, *args):
        """Runs the garbage collector."""
        items = gc.collect()
        self.logger.log(f"Done running GC ! Collected {items} items.")            

    @console_command()
    def debug(self, enabled: str = None, *args):
        """Enables or disables debug mode. Args: 'enabled' (needed)"""
        if enabled.lower() in ("true", "false"):
            enabled = enabled.lower() == "true"
            self.bot.set_debug(enabled)
            return
        self.logger.log(f"Debugging is set as '{self.logger.debugging}'."
                    " Type 'debug true/false' to enable or disable it.")

    @console_command(aliases=["log", "logging"])
    def logs(self, enabled: str = None, *args):
        """Enables or disables logs. Args: 'enabled' (needed)"""
        if enabled.lower() in ("true", "false"):
            enabled = enabled.lower() == "true"
            if enabled:
                self.logger.level = (LoggingLevel.debug
                                     if self.bot.debug_mode
                                     else LoggingLevel.info)
            else:
                self.logger.level = LoggingLevel.disabled
            return
        self.logger.log(f"Logging is set as '{self.logger.enabled}'."
                    " Type 'logs true/false' to enable or disable it.")
                

    @console_command()
    def disable(self, *args):
        """Stops the console and its thread."""
        self.logger.log("Are you sure you wanna stop the console thread ? (Y/N) :")
        response = input()
        if response.lower() in ("y", ""):
            self.running = False
            self.logger.log("Stopping console thread. Goodbye !")

    @console_command(aliases=["close"])
    def stop(self, *args):
        """Stops the bot."""
        self.logger.log("Are you sure you wanna stop the bot ? (Y/N) :")
        response = input()
        if response.lower() in ("y", ""):
            self.forcestop()

    @console_command(aliases=["adios"])
    def forcestop(self, *args):
        """Stops the bot without asking if the user is sure."""
        self.logger.log("Stopping Shibbot...")
        self.running = False
        self.bot.loop.call_soon(asyncio.ensure_future, self.bot.close(ConsoleInterruption()))
        
    # @console_command(name="exec")
    # def _exec(self, *code):
    #     """Executes some Python code."""
    #     code = " ".join(code)
    #     exec(code)
