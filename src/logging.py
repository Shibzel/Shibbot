"""Really shitty logging module, I could have used logging instead but I wanted to do it my way.

Note: Logging with a method of `Logger` takes around 3ms to run."""
from datetime import datetime
from traceback import format_exception
import os
import gzip

from src import __version__
from src.constants import LOGS_PATH, CACHE_PATH
from src.utils.json import load, dump
from src.utils.re import remove_ansi_escape_sequences


MAX_LOG_FILES = 10
LOG_EXTENSION = ".log"
LOGGER_CACHE_FILE_PATH = CACHE_PATH + "/logger_cache.json"
LATEST_LOGS_FILE_PATH = LOGS_PATH + "/latest" + LOG_EXTENSION
IS_CLOSED_KEY = "closed"
IS_ENABLED_KEY = "enabled"
IS_DEBUGGING_KEY = "debug"

if not os.path.exists(LOGGER_CACHE_FILE_PATH):
    dump({}, LOGGER_CACHE_FILE_PATH)


def load_cache():
    return load(LOGGER_CACHE_FILE_PATH)


def dump_cache():
    dump(cache, LOGGER_CACHE_FILE_PATH)


cache = load_cache()


class PStyles:
    ENDC = "\033[00m"
    WARNING = "\033[93m"
    ERROR = "\033[1;31m"
    QUIET = "\033[38;5;248m"
    OKCYAN = "\033[96m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    ITALICIZED = "\033[3m"


def log(string, **kwargs):
    """Adds text to the 'latest.log' file."""
    if cache.get(IS_ENABLED_KEY, True):
        print(string, **kwargs)
    with open(LATEST_LOGS_FILE_PATH, "a+") as f:
        clean_string = remove_ansi_escape_sequences(string)
        f.write(clean_string+"\n")


class Logger:
    """A logging class designed for Shibbot.
    
    Attributes
    ----------
    file_name: str
        The name of the file this instance is in."""

    def __init__(self, file_name: str = None):
        """Parameters
        ----------
        file_name: str
            The name of the file you're in."""
        self.file_name = file_name or "unspecified-dir"

    @property
    def enabled(*args):
        return cache.get(IS_ENABLED_KEY, False)

    @property
    def debugging(*args):
        return cache.get(IS_DEBUGGING_KEY, False)

    @staticmethod
    def formated_time(
    ) -> str: return datetime.now().strftime("%H:%M:%S.%f")[:13]

    def log(self, string: str, color: str | None = None) -> None:
        """Classic method of logging.
        Can take a 'color' argument which is a string containing an ANSI escape sequence."""
        log(f"{(color or '')}[{self.formated_time()} INFO @{self.file_name}] {string}{PStyles.ENDC}")

    def warn(self, string: str) -> None:
        """Warns the user about something."""
        log(f"{PStyles.WARNING}[{self.formated_time()} WARN @{self.file_name}] {string}{PStyles.ENDC}")

    def debug(self, string: str, error: Exception = None) -> None:
        """Prints the string if debug mode is enabled and writes to the log file whether
        debug is enabled or not.
        Use for debugging or unimportant things."""
        if not cache.get(IS_DEBUGGING_KEY):
            return
        string = f"{PStyles.QUIET}[{self.formated_time()} DEBUG @{self.file_name}] {string}{PStyles.ENDC}"
        if error:
            formated_err_lines = format_exception(type(error), error,  error.__traceback__, 1)
            string += f"\n-> {''.join(formated_err_lines)}".replace("\n\n", "\n")
        log(string)

    def error(self, string: str, error_or_traceback: str | Exception = None) -> None:
        """Prints the string in bold, bright red to indicate an error to consider.
        Can accept a traceback or an error that has been raised in order to format it."""
        string = f"{PStyles.ERROR}[{self.formated_time()} ERROR @{self.file_name}] {string}{PStyles.ENDC}"
        error_string = None
        if isinstance(error_or_traceback, Exception):
            formated_err_lines = format_exception(
                type(error_or_traceback), error_or_traceback, error_or_traceback.__traceback__, 3)
            error_string = f"-> {''.join(formated_err_lines)}".replace("\n\n", "\n")
        elif isinstance(error_or_traceback, str):
            error_string = error_or_traceback
        log(string)
        if error_string:
            log(error_string)

    @staticmethod
    def enable() -> None:
        cache[IS_ENABLED_KEY] = True
        dump_cache()
        _logger.log("Logging enabled. Hi, how have you been since ?")

    @staticmethod
    def disable() -> None:
        cache[IS_ENABLED_KEY] = False
        dump_cache()
        _logger.log(
            "Logging disabled, messages will no longer appear on the console.")

    @staticmethod
    def set_debug(boolean: bool) -> None:
        cache[IS_DEBUGGING_KEY] = boolean
        dump_cache()
        _logger.log(f"Setting debug mode for logging as '{boolean}'.")

    @staticmethod
    def start() -> None:
        """To be put at the beginning of the program."""
        logger_cache = load(LOGGER_CACHE_FILE_PATH)
        if IS_CLOSED_KEY in logger_cache and not logger_cache[IS_CLOSED_KEY]:
            _logger.debug(
                f"Closing '{LATEST_LOGS_FILE_PATH}' because the bot was not shut down properly.")
            _close()
        global cache
        cache[IS_CLOSED_KEY] = False
        if os.path.exists(LATEST_LOGS_FILE_PATH):
            os.remove(LATEST_LOGS_FILE_PATH)
        _logger.debug("~~ Starting logging.")

    @staticmethod
    def end() -> None:
        """To be put at the end of the program."""
        _logger.debug("~~ Program ended correctly.")
        _close()


def cleanup(folder_fp: str, max_files: str):
    files = os.listdir(folder_fp)
    if len(files) <= max_files:
        return 0
    sorted_by_date = sorted(files,
                            key=lambda x: os.path.getmtime(os.path.join(folder_fp, x)))
    items = len(files) - max_files
    for fichier in sorted_by_date[:items]:
        os.remove(os.path.join(folder_fp, fichier))
    return items


def _close():
    # Compressing log file.
    extension = LOG_EXTENSION + ".gz"
    raw_name = name = f"{LOGS_PATH}/{datetime.now().strftime('%Y-%m-%d')}"
    n = 1
    while os.path.exists(name+extension):
        name = f"{raw_name}+{n}"
        n += 1
    out_file = name + extension
    _logger.debug(f"Compressing '{LATEST_LOGS_FILE_PATH}' into '{out_file}'.")
    with open(LATEST_LOGS_FILE_PATH, "rb") as log_file:
        with gzip.open(out_file, "wb+") as gzip_file:
            gzip_file.write(log_file.read())
    _logger.debug("Done compressing.")
    cache[IS_CLOSED_KEY] = True
    dump_cache()
    _logger.debug(f"Cleaning up logs (will delete the oldest files if their number exceeds {MAX_LOG_FILES}).")
    if items := cleanup(LOGS_PATH, MAX_LOG_FILES):
        _logger.debug(f"Deleted {items} log file(s).")


_logger = Logger(__name__)
