"""Really shitty logging module, I could have used logging instead but I wanted to do it my way.

Note: Logging with a method of `Logger` takes around 3ms to run."""
from datetime import datetime
from traceback import format_exception
import os
import gzip

from src import __version__
from src.constants import LOGS_PATH, CACHE_PATH
from src.utils.json import load, dump


LOG_EXTENSION = ".log"
LOGGER_CACHE_FILE_PATH = CACHE_PATH + "/logger_cache.json"
LATEST_LOGS_FILE_PATH = LOGS_PATH + "/latest" + LOG_EXTENSION
IS_CLOSED_KEY = "closed"
IS_ENABLED_KEY = "enabled"
IS_DEBUGGING_KEY = "debug"

if not os.path.exists(LOGGER_CACHE_FILE_PATH):
    dump({}, LOGGER_CACHE_FILE_PATH)

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

class Logger:
    """A logging class designed for Shibbot.
    
    Attributes
    ----------
    file_name: str
        The name of the file this instance is in."""
    def __init__(self, file_name: str):
        """Parameters
        ----------
        file_name: str
            The name of the file you're in."""
        self.file_name = file_name
        
    @staticmethod
    def formated_time() -> str: return datetime.now().strftime("%H:%M:%S.%f")
    
    @staticmethod
    def _write(string):
        with open(LATEST_LOGS_FILE_PATH, "a+", encoding="utf-8") as f:
            f.write(string+"\n")
    
    @staticmethod    
    def _print(*args, **kwargs):
        if _logger.is_enabled():
            print(*args, **kwargs)

    def log(self, string: str, color: str | None = None) -> None:
        """Classic method of logging. Can take a 'color' argument which is a string containing an ANSI escape sequence."""
        string = f"[{self.formated_time()} INFO @{self.file_name}] {string}"
        self._print((color or "") + string + PStyles.ENDC)
        self._write(string)

    def debug(self, string: str) -> None:
        """Prints the string if debug mode is enabled and writes to the log file whether debug is enabled or not.
        Use for debugging or unimportant things."""
        string = f"[{self.formated_time()} DEBUG @{self.file_name}] {string}"
        logger_cache = load(LOGGER_CACHE_FILE_PATH)
        if IS_DEBUGGING_KEY in logger_cache and logger_cache[IS_DEBUGGING_KEY]:
            self._print(PStyles.QUIET + string + PStyles.ENDC)
        self._write(string)

    def warn(self, string: str) -> None:
        """Warns the user about something."""
        string = f"[{self.formated_time()} WARN @{self.file_name}] {string}"
        self._print(PStyles.WARNING + string + PStyles.ENDC)
        self._write(string)

    def error(self, string: str, error_or_traceback: str | Exception = None) -> None:
        """Prints the string in bold, bright red to indicate an error to consider.
        Can accept a traceback or an error that has been raised in order to format it."""
        string = f"[{self.formated_time()} ERROR @{self.file_name}] {string}"
        error_string = None
        if isinstance(error_or_traceback, Exception):
            error_string = f"-> {''.join(format_exception(type(error_or_traceback), error_or_traceback, error_or_traceback.__traceback__, 3))}".replace("\n\n", "")
        elif isinstance(error_or_traceback, str):
            error_string = error_or_traceback
        self._print(PStyles.ERROR + string + PStyles.ENDC)
        if error_string:
            self._print(error_string)
        self._write(string+f"\n{error_string}" if error_string else "")
    
    @staticmethod
    def _set_in_cache(key, value):
        logger_cache = load(LOGGER_CACHE_FILE_PATH)
        logger_cache[key] = value
        dump(logger_cache, LOGGER_CACHE_FILE_PATH)
        
    @staticmethod
    def is_enabled() -> bool:
        logger_cache = load(LOGGER_CACHE_FILE_PATH)
        if IS_ENABLED_KEY not in logger_cache:
            logger_cache[IS_ENABLED_KEY] = True
            dump(logger_cache, LOGGER_CACHE_FILE_PATH)
        return logger_cache[IS_ENABLED_KEY]
    
    @staticmethod
    def enable() -> None:
        _logger.debug("Logging enabled. Hi, how have you been since ?")
        _logger._set_in_cache(IS_ENABLED_KEY, True)

    @staticmethod
    def disable() -> None:
        _logger.debug("Logging disabled, messages will no longer appear on the console.")
        _logger._set_in_cache(IS_ENABLED_KEY, False)
    
    @staticmethod
    def set_debug_mode(boolean: bool) -> None:
        _logger.debug(f"Setting debug mode for logging as '{boolean}'.")
        _logger._set_in_cache(IS_DEBUGGING_KEY, boolean)
    
    @staticmethod
    def start() -> None:
        """To be put at the beginning of the program."""
        logger_cache = load(LOGGER_CACHE_FILE_PATH)
        if IS_CLOSED_KEY in logger_cache and not logger_cache[IS_CLOSED_KEY]:
            _logger.debug(f"Closing '{LATEST_LOGS_FILE_PATH}' because the bot was not shut down properly.")
            _logger._close()
        _logger._set_in_cache(IS_CLOSED_KEY, False)
        if os.path.exists(LATEST_LOGS_FILE_PATH):
            os.remove(LATEST_LOGS_FILE_PATH)
        _logger.debug(f"~~ Starting logging.")

    @staticmethod
    def end() -> None: 
        """To be put at the end of the program."""
        _logger.debug("~~ Program ended correctly.")
        _logger._close()

    @staticmethod
    def _close():
        # Compressing log file.
        extension = LOG_EXTENSION + ".gz"
        raw_name = f"{LOGS_PATH}/{datetime.now().strftime('%Y-%m-%d')}"
        if os.path.exists(raw_name+extension):
            n = 1
            while True:
                out_file = f"{raw_name}+{n}"
                if not os.path.exists(out_file+extension):
                    break
                n += 1
        else:
            out_file = raw_name
        out_file += extension
        _logger.debug(f"Compressing '{LATEST_LOGS_FILE_PATH}' into '{out_file}'.")
        with open(LATEST_LOGS_FILE_PATH, "rb") as log_file:
            with gzip.open(out_file, "wb+") as gzip_file:
                gzip_file.write(log_file.read())
        _logger.debug("Done.")
        _logger._set_in_cache("closed", True)
        
        
_logger = Logger(__name__)