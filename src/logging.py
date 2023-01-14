"""Really shitty logging module, I could have used logging instead but I wanted to do it my way.

Note: Logging with a mehtod of `Logger` takes around 3ms to run."""
from datetime import datetime
from traceback import format_exception
from os import path, remove
from gzip import open as gzip_open

from src import __version__
from src.constants import LOGS_PATH, CACHE_PATH
from src.utils.json import load, dump


LOG_EXTENSION = ".log"
LOGGER_CACHE_FILE_PATH = CACHE_PATH + "/logger_cache.json"
LATEST_LOGS_FILE_PATH = LOGS_PATH + "/latest" + LOG_EXTENSION
IS_CLOSED_KEY = "closed"
IS_ENABLED_KEY = "enabled"

if not path.exists(LOGGER_CACHE_FILE_PATH):
    dump({}, LOGGER_CACHE_FILE_PATH)

class PStyles:
    ENDC = "\033[00m"
    WARNING = "\033[93m"
    ERROR = "\033[1;31m"
    QUIET = "\033[38;5;12m"
    OKCYAN = "\033[96m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    ITALICIZED = "\033[3m"

def _print(*args, **kwargs):
    if Logger.is_enabled():
        print(*args, **kwargs)

def _write(string):
    with open(LATEST_LOGS_FILE_PATH, "a+", encoding="utf-8") as f:
        f.write(string+"\n")

def _set(key, value):
    logger_cache = load(LOGGER_CACHE_FILE_PATH)
    logger_cache[key] = value
    dump(logger_cache, LOGGER_CACHE_FILE_PATH)

def _close():
    extension = LOG_EXTENSION + ".gz"
    raw_name = f"{LOGS_PATH}/{datetime.now().strftime('%Y-%m-%d')}"
    if path.exists(raw_name+extension):
        n = 1
        while True:
            out_file = f"{raw_name}+{n}"
            if not path.exists(out_file+extension):
                break
            n += 1
    else:
        out_file = raw_name
    with open(LATEST_LOGS_FILE_PATH, "rb") as log_file:
        with gzip_open(out_file + extension, "wb+") as gzip_file:
            gzip_file.write(log_file.read())
    _set("closed", True)

class Logger:
    """This dumbass dev forgot to add a documentation."""
    def __init__(self, package_name):
        self.package_name = package_name
     
    @staticmethod   
    def is_enabled() -> bool:
        logger_cache = load(LOGGER_CACHE_FILE_PATH)
        if IS_ENABLED_KEY not in logger_cache:
            logger_cache[IS_ENABLED_KEY] = True
            dump(logger_cache, LOGGER_CACHE_FILE_PATH)
        return logger_cache[IS_ENABLED_KEY]

    @staticmethod 
    def enable() -> None:
        _set(IS_ENABLED_KEY, True)

    @staticmethod
    def disable() -> None:
        _set(IS_ENABLED_KEY, False)

    @staticmethod
    def start() -> None:
        logger_cache = load(LOGGER_CACHE_FILE_PATH)
        if IS_CLOSED_KEY in logger_cache and not logger_cache[IS_CLOSED_KEY]:
            _close()
        _set(IS_CLOSED_KEY, False)
        if path.exists(LATEST_LOGS_FILE_PATH):
            remove(LATEST_LOGS_FILE_PATH)
        _write(f"### Starting logging ({datetime.now()}) ###")

    @staticmethod
    def end() -> None: 
        _write(f"### Program ended ({datetime.now()}) ###")
        _close()
    
    @staticmethod
    def formated_time() -> str: return datetime.now().strftime("%H:%M:%S.%f")[:12]

    def log(self, string: str, color: str | None = None) -> None:
        string = f"[{self.formated_time()} INFO @{self.package_name}] {string}"
        _print((color or "") + string + PStyles.ENDC)
        _write(string)

    def quiet(self, string: str) -> None:
        string = f"[{self.formated_time()} QUIET @{self.package_name}] {string}"
        _write(string)

    def warn(self, string: str) -> None:
        string = f"[{self.formated_time()} WARN @{self.package_name}] {string}"
        _print(PStyles.WARNING + string + PStyles.ENDC)
        _write(string)

    def error(self, string: str, error_or_traceback: str | Exception = None) -> None:
        string = f"[{self.formated_time()} ERROR @{self.package_name}] {string}"
        error_string = None
        if isinstance(error_or_traceback, Exception):
            error_string = f"-> {''.join(format_exception(type(error_or_traceback), error_or_traceback, error_or_traceback.__traceback__, 3))}".replace("\n\n", "")
        elif isinstance(error_or_traceback, str):
            error_string = error_or_traceback
        _print(PStyles.ERROR + string + PStyles.ENDC)
        if error_string:
            _print(error_string)
        _write(string+f"\n{error_string}" if error_string else "")