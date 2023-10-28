import gc
import inspect
import asyncio
from typing import Iterable
from sqlite3 import ProgrammingError

from ..logging import ANSIEscape, LoggingType, SubLogger
from .. import __version__

from .errors import *


class BaseConsole:
    def __init__(self, bot):
        self.bot = bot
        self.loop: asyncio.AbstractEventLoop = bot.loop
        self.logger: SubLogger = bot.logger.get_logger(__name__)
        self.commands: dict[str, "ConsoleCommand"] = {}
        self.future = None
        self.running = False
    
    @property
    def unique_commands(self) -> dict[str, "ConsoleCommand"]:
        return {
            k: v
            for k, v in self.commands.items()
            if k == v.name
        }

    def add_command(self, command: "ConsoleCommand"):
        self.logger.debug(f"Adding command '{command.name}'.")
        names = {command.name, *command.aliases}
        if conflicted_names := names & set(self.commands):
            raise CommandNameConflict(f"The name or an alias already exists in the list of commands {tuple(conflicted_names)}.")
        mapping = {name: command for name in names}
        self.commands.update(mapping)

    def remove_command(self, command: "ConsoleCommand"):
        self.logger.debug(f"Removing command '{command.name}'.")
        for k, v in self.commands.items():
            if v.name == command.name:
                self.commands.pop(k)

    async def run(self) -> None:
        if self.running:
            raise RuntimeError("Console is already running.")
        self.logger.debug("Running console.")
        self.running = True
        while self.running:
            try:
                self.future = self.loop.run_in_executor(None, self.user_input)
                while not self.future.done():
                    if not self.running:
                        break
                    await asyncio.sleep(0.1)
                if awaitable := self.future.result():
                    await awaitable
            except ConsoleInterruption as err:
                await self.bot.close(err)
            except Exception as err:
                self.logger.error(f"Error executing command:", err)
        self.logger.debug("Console stopped.")

    def user_input(self):
        self.logger.debug("Waiting for input.")
        raw_command = input()
        args = raw_command.split(" ")
        name, args = args[0], args[1:]
        if command := self.commands.get(name):
            self.logger.debug(f"Executing command '{name}' with args: {args}")
            return command.execute(*args)  # Must be an awaitable or None
        else:
            self.logger.error(f"Unknown command '{name}'.")

    def stop(self) -> None:
        if self.future and not self.future.cancelled():
            self.logger.debug("Stopping console.")
            self.future.cancel()
        self.running = False

class ConsoleCommand:
    def __init__(
        self,
        console: BaseConsole,
        name: str,
        aliases: Iterable[str] = (),
        description: str = None,
    ):
        self.console = console
        self.bot = console.bot
        self.logger = console.logger
        self.name = name
        self.aliases = aliases
        self.description = description or self.execute.__doc__ or self.__doc__ or "No description provided."

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"

    def execute(self, *args):
        raise NotImplementedError


class HelpCommand(ConsoleCommand):
    def __init__(self, console):
        super().__init__(
            console,
            name="help",
            description="Shows all available commands."
        )

    def _format_signature(func):
        signature = inspect.signature(func)
        return [
            f"{n}: {p.__name__ if not p.empty else 'str'} ({f'default: {p.default}' if p.default else 'REQUIRED'})"
            for n, p in signature.parameters.items()
            if n != "_"
        ] or "No argument."

    def execute(self, command_name: str = None, *args):
        if not command_name:
            commands = self.console.unique_commands.values()
        else:
            if not (command := self.console.commands.get(command_name)):
                self.logger.error("Unknwown command.")
                return
            commands = [command]
        formated = "\n".join(
            f"{ANSIEscape.bold}{c.name}{ANSIEscape.endc}\n" + \
#            f"    Args: {self._format_signature(c.execute)}\n"  # TODO: Fix this code
            (f"    Aliases: {', '.join(c.aliases)}\n" if c.aliases else "") + \
            f"    Description: {c.description}"
            for c in commands)
        self.logger.info("Available commands:\n"+formated)

class InfoCommand(ConsoleCommand):
    def __init__(self, console):
        super().__init__(
            console,
            name="info",
            aliases=["botinfo", "stats", "statistics"],
            description="Shows some stats about the bot."
        )

    def execute(self, *args):
        bot = self.bot
        ut = bot.uptime
        len_guild_members = [len(guild.members) for guild in bot.guilds]
        len_users = len(bot.users)
        len_members = sum(len_guild_members)
        self.logger.log(
            f"{ANSIEscape.bold}Program :{ANSIEscape.endc}\n"
            f"    Core version: v{__version__}\n"
            f"    Uptime: {ut.days}d {ut.hours}h {ut.minutes}m {ut.seconds}s\n"
            f"    Cogs: {len(bot.cogs)} ({len(bot.plugins)} plugins)\n"
            f"    Ping: {round(bot.latency*1000, 2)}ms\n"
            f"    Average processing time: {bot.avg_processing_time:.2f}ms\n"
            f"    Invoked commands: {bot.invoked_commands}\n"
            f"{ANSIEscape.bold}User :{ANSIEscape.endc}\n"
            f"    Guilds: {len(bot.guilds)}\n"
            f"    Members: {len_members}\n"
            f"    Users: {len_users} ({round(len_users/len_members*100, 2)}%)\n"
            f"    Biggest server: {max(len_guild_members)} members"
        )

class PingCommand(ConsoleCommand):
    def __init__(self, console):
        super().__init__(
            console,
            name="ping",
            description="Returns the ping of the bot."
        )

    def execute(self, *_):
        self.logger.log(f"Ping: {round(self.bot.latency*1000, 2)}ms.")

class UptimeCommand(ConsoleCommand):
    def __init__(self, console):
        super().__init__(
            console,
            name="uptime",
            aliases=["ut"],
            description="Shows the uptime."
        )

    def execute(self, *_):
        uptime = self.bot.uptime
        self.logger.log(f"Up for: {uptime.days} days, {uptime.hours} hours,"
                        f" {uptime.minutes} min and {uptime.seconds} sec.")
        
class ShowCogsCommand(ConsoleCommand):
    def __init__(self, console):
        super().__init__(
            console,
            name="cogs",
            description="Shows all the enabled cogs."
        )

    def execute(self, *_):
        # TODO: Improve code
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

class _OnCog(ConsoleCommand):
    def _apply_on_cog(self, method, method_name, cog_name):
        async def wrapper():
            try:
                method(cog_name)  # Must be executed in the main thread
                self.logger.log(f"Successfully {method_name}ed '{cog_name}'.")
            except ProgrammingError as exc:
                raise exc
            except Exception as err:
                self.logger.error(f"Could not {method_name} '{cog_name}'.", err)
        return wrapper()
    
class LoadCommand(_OnCog):
    def __init__(self, console):
        super().__init__(
            console,
            name="load",
            description="Loads a cog."
        )

    def execute(self, cog_name, *_):
        return self._apply_on_cog(self.bot.load_extension, "load", cog_name)

class UnloadCommand(_OnCog):
    def __init__(self, console):
        super().__init__(
            console,
            name="unload",
            description="Unloads a cog."
        )

    def execute(self, cog_name, *_):
        return self._apply_on_cog(self.bot.unload_extension, "unload", cog_name)

class ReloadCommand(_OnCog):
    def __init__(self, console):
        super().__init__(
            console,
            name="reload",
            description="Reloads a cog."
        )

    def execute(self, cog_name, *_):
        return self._apply_on_cog(self.bot.reload_extension, "reload", cog_name)

class GcCommand(ConsoleCommand):
    def __init__(self, console):
        super().__init__(
            console,
            name="gc",
            description="Runs the garbage collector."
        )

    def execute(self, *_):
        items = gc.collect()
        self.logger.log(f"Done running GC ! Collected {items} items.")
        
class DisableConsoleCommand(ConsoleCommand):
    def __init__(self, console):
        super().__init__(
            console,
            name="disable",
            description="Stops the console and its thread."
        )

    def execute(self, *_):
        self.logger.info("Disabling console, goodbye !")
        self.console.stop()

class DebugCommand(ConsoleCommand):
    def __init__(self, console):
        super().__init__(
            console,
            name="debug",
            description="Enables or disables debug mode."
        )

    def execute(self, enabled: bool = "", *_):
        if enabled.lower() in ("true", "false"):
            enabled = enabled.lower() == "true"
            self.bot.debug_mode = enabled
            return
        level = self.logger.level
        self.logger.log(f"Debug level is set as '{LoggingType[level]}' ({level})."
                        " Type 'debug true/false' to enable or disable debug.")

class StopCommand(ConsoleCommand):
    def __init__(self, console):
        super().__init__(
            console,
            name="stop",
            aliases=["adios", "^C"],
            description="Stops the bot."
        )

    def execute(self, *_):
        self.logger.log("Stopping Shibbot...")
        raise ConsoleInterruption
    

class Console(BaseConsole):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_command(HelpCommand(self))
        self.add_command(InfoCommand(self))
        self.add_command(PingCommand(self))
        self.add_command(ShowCogsCommand(self))
        self.add_command(LoadCommand(self))
        self.add_command(UnloadCommand(self))
        self.add_command(ReloadCommand(self))
        self.add_command(GcCommand(self))
        self.add_command(DebugCommand(self))
        self.add_command(DisableConsoleCommand(self))
        self.add_command(StopCommand(self))