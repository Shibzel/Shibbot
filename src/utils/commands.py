import discord
from discord.ext import commands
from .language import get_language


def get_name_localization(obj, lang_code: str) -> str | None:
    obj_name = None
    if getattr(obj, "name_localizations", None) and obj.name_localizations.get(lang_code):
        obj_name = get_language(obj.name_localizations, lang_code)
    return obj_name if obj_name else obj.name
    
def get_description_localization(obj, lang_code: str) -> str | None:
    obj_description = None
    if getattr(obj, "description_localizations", None) and obj.description_localizations.get(lang_code):
        obj_description = get_language(obj.description_localizations, lang_code)
    return obj_description if obj_description else obj.description

def stringify_command_usage(command: discord.SlashCommand | commands.Command, lang_code: str) -> str | None:
    command_options = ""
    if isinstance(command, discord.SlashCommand):
        for option in command.options:
            option_name = get_name_localization(option, lang_code)
            command_options += f" [{option_name}]" if option.required else f" <{option_name}>"
    elif isinstance(command, commands.Command):
        for name, inspct in command.clean_params.items():
            command_options += f" [{name}]" if inspct.default else f" <{name}>"
    return f"{command.name}{command_options}"
