from discord import Member
from discord.ext import commands

from . import __version__


__all__ = ("PrefixedNotAvailable", "PluginDisabledError", "MissingArgumentsError",
           "NotInteractionOwner", "ServiceUnavailableError", "CogDependanceMissing",
           "DeprecatedBotError")


class ShibbotBaseError(Exception):
    """Base error exception for Shibbot."""
    pass

class PrefixedNotAvailable(ShibbotBaseError, commands.CommandError):
    pass

class PluginDisabledError(ShibbotBaseError, commands.CheckFailure):
    """Raised when the user is trying to use a commands belonging to a disabled plugin."""
    def __init__(self, plugin_name: str, message: str = None):
        self.plugin_name = plugin_name
        super().__init__(message or f"The '{plugin_name}' plugin is disabled.")

class MissingArgumentsError(ShibbotBaseError, commands.CheckFailure):
    """Raised when the user did not fulfill the requirements of a command."""
    def __init__(self, command: commands.Command, error_case_msg: str = None, message: str = None):
        self.command = command
        self.error_case_msg = error_case_msg
        if isinstance(self.command, commands.Command):
            for cog_command in self.command.cog.get_commands():
                if cog_command.name == self.command.name:
                    self.command = cog_command
                    break
        self.message = message
        super().__init__(self.message or f"Missing arguments for command '{self.command.name}'.")

class NotInteractionOwner(ShibbotBaseError, commands.UserInputError):
    """Raised when an user tries to interact with an interaction that don't belong to him."""
    def __init__(self, interaction_owner: Member, user_interacting: Member,
                 message: str = None):
        self.interaction_owner = interaction_owner
        self.user_interacting = user_interacting
        super().__init__(message or f"'{user_interacting}' doesn't have access"
                         f" to this interaction, it belongs to '{interaction_owner}'.")

class ServiceUnavailableError(ShibbotBaseError, commands.CommandError):
    """Raised when a service is unavailable."""

class CogDependanceMissing(ShibbotBaseError):
    """Raised when a cog is missing dependecies."""
    def __init__(self, cog_name: str = None, message: str = None):
        super().__init__(message or "This cog depends on another." + \
                         ("" if not cog_name else f" Missing Cog: {cog_name}."))

class DeprecatedBotError(ShibbotBaseError):
    """Raised when the bot or the extension is deprecated."""
    def __init__(self, min_version: str, cog_name: str = None, message: str = None):
        if not message:
            cog = "This cog" if not cog_name else f"'{cog_name}"
            message = f"{cog} cannot be loaded because this version of Shibbot" + \
                      f" is deprecated (cog: {min_version}, shibbot: {__version__})."
        super().__init__(message)
