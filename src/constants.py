DEFAULT_PREFIX = "$"
DEFAULT_LANGUAGE = "en"

DATABASE_FILE_PATH = "./database.sqlite3"
LOGS_PATH = "./logs"
CACHE_PATH = "./cache"
TEMPORARY_CACHE_PATH = CACHE_PATH + "/temp"

COGS_PATH = "./src/cogs"
EXTENSIONS_PATH = "./extensions"
CORE_COGS = ("commands", "events",)
OPTIONAL_COGS = (
    "owner",
    "status",
    # "mod",
    # "automod",
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
