from discord import Member
from discord.ext import commands

from . import __version__


class PluginDisabledError(commands.CheckFailure):
    """Raised when the user is trying to use a commands belonging to a disabled plugin."""

    def __init__(self, plugin_name: str, message: str | None = None):
        self.plugin_name = plugin_name
        super().__init__(message or f"The '{plugin_name}' plugin is disabled.")


class MissingArgumentsError(commands.CheckFailure):
    """Raised when the user did not fulfill the requirements of a command."""

    def __init__(self, command: commands.Command, error_case_msg: str | None = None, message: str | None = None):
        self.command = command
        self.error_case_msg = error_case_msg
        if isinstance(self.command, commands.Command):
            for cog_command in self.command.cog.get_commands():
                if cog_command.name == self.command.name:
                    self.command = cog_command
                    break
        self.message = message
        super().__init__(
            self.message or f"Missing arguments for command '{self.command.name}'.")


class NotInteractionOwner(commands.UserInputError):
    """Raised when an user tries to interact with an interaction that don't belong to him."""

    def __init__(self, interaction_owner: Member, user_interacting: Member, message: str | None = None):
        self.interaction_owner = interaction_owner
        self.user_interacting = user_interacting
        super().__init__(message or f"'{user_interacting}' doesn't have access"
                         f" to this interaction, it belongs to '{interaction_owner}'.")


class ServiceUnavailableError(commands.CommandError):
    """Raised when a service is unavailable."""

    def __init__(self, message: str | None = None):
        super().__init__(message)


class CogDependanceMissing(Exception):
    """Raised when a cog is missing dependecies."""

    def __init__(self, cog_name: str | None = None, message: str | None = None):
        super().__init__(message or "This cog depends on another."
                         ("" if not cog_name else f" Missing Cog: {cog_name}."))


class DeprecatedBotError(Exception):
    """Raised when the bot is deprecated and cannot load an extension."""

    def __init__(self, min_version: str, cog_name: str | None = None, message: str | None = None):
        if not message:
            cog = "This cog" if not cog_name else f"'{cog_name}"
            message = f"{cog} cannot be loaded because this version of Shibbot" + \
                      f" is deprecated (cog: {min_version}, shibbot: {__version__})."
        super().__init__(message)


class PluginWithSameNameError(Exception):
    """Raised when a plugin with the same name as another is trying to load."""

    def __init__(self, plugin=None, confilcted_plugin=None, message: str | None = None):
        if not message:
            plugin_name = "This plugin extension" if not plugin else f"'{plugin.__name__}'"
            conf_plugin_name = ("another plugin" 
                                if not confilcted_plugin else f"'{confilcted_plugin.__name__}'")
            name = f" : '{plugin.plugin_name}'" if plugin and confilcted_plugin else ""
            message = f"{plugin_name} has the plugin name for the database as {conf_plugin_name}{name}." + \
                        " Please change the name or contact the developper" + \
                        " of the extension to correct this conflict."
        super().__init__(message)
