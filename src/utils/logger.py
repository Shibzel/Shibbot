import datetime
import traceback

from src.constants import LOGS_PATH


def _write(string):
    with open(f"{LOGS_PATH}/{datetime.datetime.now().strftime('%Y-%m-%d')}.log", "a+", encoding="utf-8") as f:
        f.write(string+"\n")

class Logger:
    """This dumbass dev forgot to add a documentation."""
    def __init__(self, package_name):
        self.package_name = package_name

    @staticmethod
    def formated_time(): return datetime.datetime.now().strftime("%H:%M:%S.%f")[:12]

    def log(self, string):
        string = f"[{Logger.formated_time()} INFO @{self.package_name}] {string}"
        print(string)
        _write(string)

    def quiet(self, string):
        _write(f"[{Logger.formated_time()} QUIET @{self.package_name}] {string}")

    def warn(self, string):
        string = f"[{Logger.formated_time()} WARN @{self.package_name}] {string}"
        print(f"\033[93m{string}\033[00m")
        _write(string)

    def error(self, string, error=None):
        string = f"[{Logger.formated_time()} ERROR @{self.package_name}] {string}"
        print(f"\033[91m{string}\033[00m")
        error_string = None
        if error:
            error_string = "  ".join(traceback.format_exception(type(error), error, error.__traceback__, 3)).replace("\n\n", "")
            error_string = f"-> {error_string}"
            print(error_string)
        _write(string+f"\n{error_string}" if error_string else "")

    @staticmethod
    def start(): _write(f"### Starting logging ({datetime.datetime.now()}) ###")

    @staticmethod
    def end(): _write(f"### Program stopped corectly ({datetime.datetime.now()}) ###")