
class ConsoleError(Exception):
    pass

class ConsoleInterruption(ConsoleError):
    """Raised when the bot is stopping because of an user interaction."""
    def __init__(self, message: str = None):
        super().__init__(message or "Shibbot was asked to stop by the console.")

class CommandNameConflict(ConsoleError):
    def __init__(self, message: str = None):
        super().__init__(message or "Command already exists.")