"""Really shitty logging module, I could have used logging instead but I wanted to do it my way.

Note: Logging with a method of `Logger` takes around 3ms to run."""
import os
import gzip
from datetime import datetime
from traceback import format_exception

from src import __version__
from src.utils.re import remove_ansi_escape_sequences


__all__ = ("LOG_EXTENSION", "LATEST_LOG_FILE_NAME", "END_CHARACTER", "ENCODING", "ANSIEscape"
           "LoggingLevel", "format_error", "cleanup", "BaseLogger", "Logger", "SubLogger")


LOG_EXTENSION = ".log"
LATEST_LOG_FILE_NAME = "/latest" + LOG_EXTENSION
END_CHARACTER = "ඞ"  # Don't ask questions
ENCODING = "UTF-8"

class ANSIEscape:
    """Collection of ANSI escape sequences for coloration or text formating."""
    endc = "\033[00m"
    cyan = "\033[96m"
    blue = "\033[94m"
    green = "\033[92m"
    gray = "\033[38;5;248m"
    orange = "\033[93m"
    red = "\033[1;31m"
    red_font = "\033[48;5;196m"
    bold = "\033[1m"
    underline = "\033[4m"
    italicize = "\033[3m"
    
class LoggingLevel:
    """Self-explanatory, collection of logging levels."""
    debug = 4
    log = info = information = 3
    warn = warning = 2
    error = 1
    critical = fatal = 0
    disabled = -1

# The type can be retuned thanks to the index
# >>> level = LoggingLevel.log  # int: 3
# >>> LoggingType(level)
# Output: INFO
LoggingType = ("CRITICAL", "ERROR", "WARN", "INFO", "DEBUG")

def format_error(error_or_traceback: str | Exception, limit: int = 3, **kwargs) -> str:
    """Formats en error. If the error is already an string it's immediatly returned."""
    if not error_or_traceback:
        return ""
    if not isinstance(error_or_traceback, Exception):
        return "\n"+str(error_or_traceback)
    
    formated_err_lines = format_exception(
        type(error_or_traceback),
        error_or_traceback,
        error_or_traceback.__traceback__,
        limit=limit,
        **kwargs)
    error_string = f"\n-> {''.join(formated_err_lines)}"
    return error_string.replace("\n\n", "\n")
        
def cleanup(folder_path: str, max_files: str):
    """Deletes the oldests files if an limit is exceeded."""
    files = os.listdir(folder_path)
    if len(files) < max_files:
        return 0
    sorted_by_date = sorted(
        files,
        key=lambda x: os.path.getmtime(folder_path + f"/{x}"))
    items = len(files) - max_files
    for fichier in sorted_by_date[:items]:
        os.remove(os.path.join(folder_path, fichier))
    return items

class BaseLogger:
    """Primitive logger."""
    
    def __init__(
            self,
            module: str,
            file: str,
            level: int,
            time_format: str,
            instance_name: str = None,
        ) -> None:
        self.module = module
        self.file = file
        self.time_format = time_format
        self.level = level
        self.instance_name = instance_name
    
    def formated_time(self, override: str = None) -> str:
        return datetime.now().strftime(override or self.time_format)
        
    def _log(self, level: int, msg: str, color: str = None) -> None:
        msg = f"{color or ''}[{self.formated_time()} {LoggingType[level]} @{self.module}] {msg} {ANSIEscape.endc}"
        
        if self.instance_name:
            print(f"[{self.instance_name}]", end="")
        print(msg)
        with open(self.file, "a+", encoding=ENCODING) as f:
            clean_string = remove_ansi_escape_sequences(msg)
            f.write(clean_string+"\n")
                
    def debug(self, msg: str, error: str | Exception = None) -> None:
        if self.level >= LoggingLevel.debug:
            msg += ANSIEscape.endc + format_error(error)
            self._log(LoggingLevel.debug, msg, ANSIEscape.gray)
    
    def info(self, msg: str, color: str = None) -> None:
        if self.level >= LoggingLevel.info:
            self._log(LoggingLevel.info, msg, color)
            
    def log(self, msg: str, color: str = None) -> None:
        self.info(msg, color)
    
    def warn(self, msg: str) -> None:
        if self.level >= LoggingLevel.warn:
            self._log(LoggingLevel.warn, msg, ANSIEscape.orange)
    
    def error(self, msg: str, error: str | Exception = None) -> None:
        if self.level >= LoggingLevel.error:
            msg += ANSIEscape.endc + format_error(error)
            self._log(LoggingLevel.error, msg, ANSIEscape.red)
    
    def critical(self, msg: str, error: str | Exception = None) -> None:
        if self.level >= LoggingLevel.critical:
            msg += ANSIEscape.endc + format_error(error, limit=None)
            self._log(LoggingLevel.critical, msg, ANSIEscape.red_font)

class Logger(BaseLogger):    
    def __init__(
            self,
            path: str,
            module: str,
            level: int = LoggingLevel.info,
            time_format: str = "%Y-%d-%m %H:%M",
            max_logs: int = 10,
            instance_name: str = None,
        ):
        self.path = path
        os.makedirs(path, exist_ok=True)
        self.max_logs = max_logs
        self.instance_name = instance_name
        super().__init__(
            file=path+LATEST_LOG_FILE_NAME,
            module="main" if module == "__main__" else module,
            level=level,
            time_format=time_format,
            instance_name=instance_name
        )
        
        with open(self.file, "r+", encoding="utf-8") as f:
            if f.readlines()[-1] != END_CHARACTER:
                self.debug("Program did not shut down corectly, closing...")
                self.close()
        os.remove(self.file)  # Removes the file
        self.info("Starting logging.")  # But not explicitly recreated here
        
    def __enter__(self) -> "Logger":
        return self
    
    def __exit__(self, *args) -> None:
        self.close()
        
    def get_logger(self, module: str = "unspecified-dir") -> "SubLogger":
        return SubLogger(self, module)
        
    def close(self) -> None:
        self.info(f"Stopping logging.")
        self.debug("Cleaning up logs.")
        if items := cleanup(self.path, self.max_logs):
            self.debug(f"Deleted {items} log file(s).")
            
        extension = LOG_EXTENSION + ".gz"
        raw_name = f"{self.path}/{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        out_file = raw_name + extension
        n = 0
        while os.path.exists(out_file):
            n += 1
            out_file = f"{raw_name}+{n}{extension}"
        self.debug(f"Compressing {self.file} into {out_file}...")
        with open(self.file, "rb") as log_file:
            with gzip.open(out_file, "wb+") as gzip_file:
                gzip_file.write(log_file.read())
        with open(self.file, "a", encoding="utf-8") as log_file:
            log_file.write(END_CHARACTER)
        
class SubLogger(BaseLogger):
    """Subclass of `BaseLogger`. Primitive logger generated by the get_logger() method on `Logger`."""
    
    def __init__(self, logger: Logger, module: str):
        self._logger = logger
        self.module = module
        self.instance_name = logger.instance_name
        self.get_logger = self._logger.get_logger
        
    @property
    def file(self) -> str:        # I don't know any other way to share the same
        return self._logger.file  # attribute than wrapping it like this
        
    @property
    def time_format(self) -> str:
        return self._logger.time_format
        
    @property
    def level(self) -> str:
        return self._logger.level
