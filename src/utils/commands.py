import discord
from .language import get_language


def get_name_localization(obj, lang_code: str) -> str | None:
    obj_name = None
    if obj.name_localizations and obj.name_localizations.get(lang_code):
            obj_name = get_language(obj.name_localizations, lang_code)
    return obj_name if obj_name else obj.name
    
def get_description_localization(obj, lang_code: str) -> str | None:
    obj_description = None
    if obj.description_localizations and obj.description_localizations.get(lang_code):
            obj_description = get_language(obj.description_localizations, lang_code)
    return obj_description if obj_description else obj.description


def stringify_command_usage(command: discord.SlashCommand, lang_code: str) -> str | None:
    command_options = ""
    for option in command.options:
        option_description = get_name_localization(option, lang_code)
        command_options += f" [{option_description}]" if option.required else f" <{option_description}>"
    return f"{command.name}{command_options}"
