from datetime import datetime
from traceback import format_exception
from os import rename, path, remove
from shutil import copyfile
from gzip import open as gzip_open

from src import __version__
from src.constants import LOGS_PATH, CACHE_PATH
from src.utils.json import load, dump


LOG_EXTENSION = ".log"
LOGGER_CACHE_FILE_PATH = CACHE_PATH + "/logger_cache.json"
LATEST_LOGS_FILE_PATH = LOGS_PATH + "/latest" + LOG_EXTENSION
if not path.exists(LOGGER_CACHE_FILE_PATH):
    dump({}, LOGGER_CACHE_FILE_PATH)
logger_cache = load(LOGGER_CACHE_FILE_PATH)

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

def _write(string):
    with open(LATEST_LOGS_FILE_PATH, "a+") as f:
        f.write(string+"\n")
        
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
    out_file = out_file
    with open(LATEST_LOGS_FILE_PATH, "rb") as log_file:
        with gzip_open(f"{out_file}{extension}", "wb+") as gzip_file:
            gzip_file.write(log_file.read())
    logger_cache["closed"] = True
    dump(logger_cache, LOGGER_CACHE_FILE_PATH)

class Logger:
    """This dumbass dev forgot to add a documentation."""
    def __init__(self, package_name):
        self.package_name = package_name

    @staticmethod
    def start():
        global logger_cache
        if "closed" in logger_cache and not logger_cache["closed"]:
            _close()
        if path.exists(LATEST_LOGS_FILE_PATH):
            remove(LATEST_LOGS_FILE_PATH)
        logger_cache["closed"] = False
        dump(logger_cache, LOGGER_CACHE_FILE_PATH)
        _write(f"### Starting logging ({datetime.now()}) ###")

    @staticmethod
    def end(): 
        _write(f"### Program ended ({datetime.now()}) ###")
        _close()
    
    @staticmethod
    def formated_time(): return datetime.now().strftime("%H:%M:%S.%f")[:12]

    def log(self, string):
        string = f"[{Logger.formated_time()} INFO @{self.package_name}] {string}"
        print(string)
        _write(string)

    def quiet(self, string):
        string = f"[{Logger.formated_time()} QUIET @{self.package_name}] {string}"
        print(PStyles.QUIET + string + PStyles.ENDC)
        _write(string)

    def warn(self, string):
        string = f"[{Logger.formated_time()} WARN @{self.package_name}] {string}"
        print(PStyles.WARNING + string + PStyles.ENDC)
        _write(string)

    def error(self, string, error=None):
        string = f"[{Logger.formated_time()} ERROR @{self.package_name}] {string}"
        print(PStyles.ERROR + string + PStyles.ENDC)
        error_string = None
        if error:
            error_string = "  ".join(format_exception(type(error), error, error.__traceback__, 3)).replace("\n\n", "")
            error_string = f"-> {error_string}"
            print(error_string)
        _write(string+f"\n{error_string}" if error_string else "")