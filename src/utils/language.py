from discord.ext import bridge

from src import database
from src.constants import DEFAULT_LANGUAGE


def get_language(_dict: dict, lang_code: str) -> list:
    if _dict.get(lang_code):
        return _dict[lang_code]
    elif _dict.get(DEFAULT_LANGUAGE):
        return _dict[DEFAULT_LANGUAGE]
    else:
        return list(_dict.values())[0] if len(_dict.values()) != 0 else None


async def factory_language(ctx: bridge.BridgeApplicationContext, languages_dict: dict):
    lang_code = await database.get_language(ctx)
    return get_language(languages_dict, lang_code)

fl = factory_language
