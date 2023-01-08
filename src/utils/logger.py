from datetime import datetime
from traceback import format_exception

from src.constants import LOGS_PATH


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
    with open(f"{LOGS_PATH}/{datetime.now().strftime('%Y-%m-%d')}.log", "a+", encoding="utf-8") as f:
        f.write(string+"\n")

class Logger:
    """This dumbass dev forgot to add a documentation."""
    def __init__(self, package_name):
        self.package_name = package_name

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

    @staticmethod
    def start(): _write(f"### Starting logging ({datetime.now()}) ###")

    @staticmethod
    def end(): _write(f"### Program stopped corectly ({datetime.now()}) ###")