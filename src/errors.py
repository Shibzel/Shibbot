import discord
from discord.ext import commands, bridge


class PluginDisabledError(commands.CheckFailure):

    def __init__(self, plugin_name: str, message: str | None = None):
        self.plugin_name = plugin_name
        super().__init__(message or f"The '{plugin_name}' plugin is disabled.")


class MissingArgumentsError(commands.CheckFailure):

    def __init__(self, command: bridge.BridgeExtCommand | bridge.BridgeSlashCommand, message: str | None = None):
        self.command = command
        if isinstance(self.command, bridge.BridgeExtCommand):
            for cog_command in self.command.cog.get_commands():
                if cog_command.name == self.command.name:
                    self.command = cog_command
        super().__init__(message or f"Missing arguments for command '{self.command.name}'.")


class NotInteractionOwner(commands.UserInputError):

    def __init__(self, interaction_owner: discord.Member, user_interacting: discord.Member, message: str | None = None):
        self.interaction_owner = interaction_owner
        self.user_interacting = user_interacting
        super().__init__(message or f"'{user_interacting}' doesn't have access to this interaction, it belongs to '{interaction_owner}'.")