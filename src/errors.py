from discord import SlashCommand, Member
from discord.ext import commands

from . import __version__


class PluginDisabledError(commands.CheckFailure):
    def __init__(self, plugin_name: str, message: str | None = None):
        self.plugin_name = plugin_name
        super().__init__(message or f"The '{plugin_name}' plugin is disabled.")

class MissingArgumentsError(commands.CheckFailure):
    def __init__(self, command: commands.Command, message: str | None = None):
        self.command = command
        if isinstance(self.command, commands.Command):
            for cog_command in self.command.cog.get_commands():
                if cog_command.name == self.command.name:
                    self.command = cog_command
                    break
        self.message = message
        super().__init__(self.message or f"Missing arguments for command '{self.command.name}'.")

class NotInteractionOwner(commands.UserInputError):
    def __init__(self, interaction_owner: Member, user_interacting: Member, message: str | None = None):
        self.interaction_owner = interaction_owner
        self.user_interacting = user_interacting
        super().__init__(message or f"'{user_interacting}' doesn't have access to this interaction, it belongs to '{interaction_owner}'.")

class ServiceUnavailableError(commands.CommandError):
    def __init__(self, message: str | None = None):
        super().__init__(message)
        
class CogDependanceMissing(Exception):
    def __init__(self, cog_name: str | None = None, message: str | None = None):
        super().__init__(message or "This cog depends on another."+("" if not cog_name else f" Missing Cog: {cog_name}."))
        
class DeprecatedBotError(Exception):
    def __init__(self, min_version: str, cog_name: str | None = None, message: str | None = None):
        if not message:
            message = f"{0} cannot be loaded because this version of Shibbot is deprecated (cog: {min_version}, shibbot: {__version__}).".format(
                      "This cog" if not cog_name else f"'{cog_name}")
        super().__init__(message)
        
class PluginWithSameNameError(Exception):
    def __init__(self, plugin = None, confilcted_plugin = None, message: str | None = None):
        if not message:
            message = f"{0} has the plugin name for the database as {1}{3}. Please change the name or contact the developper of the extension to correct this conflict.".format(
                "This plugin extension" if not plugin else f"'{plugin.__name__}'",
                "another plugin" if not confilcted_plugin else f"'{confilcted_plugin.__name__}'",
                f" : '{plugin.plugin_name}'" if plugin and confilcted_plugin else "")
        super().__init__(message)