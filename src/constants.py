__all__ = ("DEFAULT_PREFIX", "DEFAULT_LANGUAGE", "COGS_PATH", "CORE_COGS",
           "OPTIONAL_COGS", "BUILTIN_COGS", "LANGUAGES", "LANGUAGES_FLAGS",
           "SHIBZEL_ID", "SERVER_INVITATION_LINK", "DATABASE_FILE_PATH",
           "LOGS_PATH", "CACHE_PATH", "TEMPORARY_CACHE_PATH", "EXTENSIONS_PATH")


DEFAULT_PREFIX = "$"
DEFAULT_LANGUAGE = "en"

COGS_PATH = "./src/cogs"
CORE_COGS = ("commands", "events",)
OPTIONAL_COGS = (
    "admin",
    "status",
    "mod",
    "automod",
    "fun",
    "utils",
    # "music",
    "misc",
)
BUILTIN_COGS = CORE_COGS + OPTIONAL_COGS

LANGUAGES = {
    "shibberish": "Shibberish", # Similar to "LolCat"
    "fr": "French",
    "en": "English",
    "es": "Spanish",
    "de": "German",
    "pt": "Portuguese",
    "zh": "Chinese",
    "ko": "Korean",
    "ja": "Japanese",
    "ar": "Arabic",
    "ru": "Russian",
    "it": "Italian",
    "nl": "Dutch",
    "tr": "Turkish",
    "sv": "Swedish",
    "pl": "Polish",
    "ro": "Romanian",
    "uk": "Ukrainian",
    "cs": "Czech",
    "hu": "Hungarian",
    "fi": "Finnish",
    "no": "Norwegian",
    "da": "Danish",
    "hi": "Hindi",
    "th": "Thai",
    "vi": "Vietnamese",
    "id": "Indonesian",
    "ms": "Malay",
    "tl": "Tagalog",
    "fa": "Persian",
    "he": "Hebrew",
    "el": "Greek",
    "bg": "Bulgarian",
    "sr": "Serbian",
    "hr": "Croatian",
    "sk": "Slovak",
    "sl": "Slovenian",
    "et": "Estonian",
    "lv": "Latvian",
    "lt": "Lithuanian",
    # "language code": "language name",
}
LANGUAGES_FLAGS = {
    "shibberish": "💬",
    "fr": "🇫🇷",
    "en": "🇬🇧",
    "es": "🇪🇸",
    "de": "🇩🇪",
    "pt": "🇵🇹",
    "zh": "🇨🇳",
    "ko": "🇰🇷",
    "ja": "🇯🇵",
    "ar": "🇸🇦",
    "ru": "🇷🇺",
    "it": "🇮🇹",
    "nl": "🇳🇱",
    "tr": "🇹🇷",
    "sv": "🇸🇪",
    "pl": "🇵🇱",
    "ro": "🇷🇴",
    "uk": "🇺🇦",
    "cs": "🇨🇿",
    "hu": "🇭🇺",
    "fi": "🇫🇮",
    "no": "🇳🇴",
    "da": "🇩🇰",
    "hi": "🇮🇳",
    "th": "🇹🇭",
    "vi": "🇻🇳",
    "id": "🇮🇩",
    "ms": "🇲🇾",
    "tl": "🇵🇭",
    "fa": "🇮🇷",
    "he": "🇮🇱",
    "el": "🇬🇷",
    "bg": "🇧🇬",
    "sr": "🇷🇸",
    "hr": "🇭🇷",
    "sk": "🇸🇰",
    "sl": "🇸🇮",
    "et": "🇪🇪",
    "lv": "🇱🇻",
    "lt": "🇱🇹",
    # "language code": "flag emoji",
}

SHIBZEL_ID = 380044496370532353
SERVER_INVITATION_LINK = "https://discord.gg/TZNWfJmPwj"
OFFICIAL_SHIBBOT_INSTANCES = (
    838922957547765801,  # Production
    848729671083360316  # Beta
)

DATABASE_FILE_PATH = "./database.db"
LOGS_PATH = "./logs"
CACHE_PATH = "./cache"
TEMPORARY_CACHE_PATH = CACHE_PATH + "/temp"
EXTENSIONS_PATH = "./extensions"
