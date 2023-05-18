from discord.ext import bridge

from ..constants import DEFAULT_LANGUAGE
from ..database import is_or_has_guild


def get_language(_dict: dict, lang_code: str) -> list:
    """Returns the value corresponding to the language, by the default language 
    if there is no corresponding key or by the first value if the default language has no value either.

    Parameters
    ----------
    _dict: `dict`
    lang_code: `str`

    Returns
    -------
    `object`: The value corresponding to the language.
    """
    if _dict.get(lang_code):
        return _dict[lang_code]
    elif _dict.get(DEFAULT_LANGUAGE):
        return _dict[DEFAULT_LANGUAGE]
    else:
        return list(_dict)[0] if len(_dict) else None


def factory_language(bot, ctx: bridge.BridgeApplicationContext, languages_dict: dict):
    """Get the language from the database with the context and return the corresponding value using the `.get_language` function.

    Args:
    ctx: `bridge.BridgeApplicationContext`
    languages_dict: `dict`

    Returns:
    `object`: The value corresponding to the language.
    """
    guild = is_or_has_guild(ctx)
    lang_code = bot.db.get_language(guild)
    return get_language(languages_dict, lang_code)

fl = factory_language
