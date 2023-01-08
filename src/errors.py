from discord import SlashCommand, Member
from discord.ext import commands


class PluginDisabledError(commands.CheckFailure):
    def __init__(self, plugin_name: str, message: str | None = None):
        self.plugin_name = plugin_name
        super().__init__(message or f"The '{plugin_name}' plugin is disabled.")

class MissingArgumentsError(commands.CheckFailure):
    def __init__(self, command: commands.Command | SlashCommand, message: str | None = None):
        self.command = command
        self.message = message
        if isinstance(self.command, commands.Command):
            for cog_command in self.command.cog.get_commands():
                if cog_command.name == self.command.name:
                    self.command = cog_command
        super().__init__(self.message or f"Missing arguments for command '{self.command.name}'.")

class NotInteractionOwner(commands.UserInputError):
    def __init__(self, interaction_owner: Member, user_interacting: Member, message: str | None = None):
        self.interaction_owner = interaction_owner
        self.user_interacting = user_interacting
        super().__init__(message or f"'{user_interacting}' doesn't have access to this interaction, it belongs to '{interaction_owner}'.")

class CogDependanceMissing(Exception):
    def __init__(self, message: str | None = None, cog_name: str | None = None):
        super().__init__(message or "This cog depends on another."+("" if not cog_name else f" Missing Cog: {cog_name}."))

class ServiceUnavailableError(commands.CommandError):
    def __init__(self, message: str | None):
        super().__init__(message)