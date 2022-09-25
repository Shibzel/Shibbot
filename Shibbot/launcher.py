"""Starts the bot with a beautiful ASCII art."""
from bot import Shibbot, __version__

if __name__ == "__main__":
    print(
        f" ________________________________\n|░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|\n|░░░█▀▀░█░█░▀█▀░█▀▄░█▀▄░█▀█░▀█▀░░|\n"
        f"|░░░▀▀█░█▀█░░█░░█▀▄░█▀▄░█░█░░█░░░|\n|░░░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░░▀░░░|\n"
        f"|░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|\n --------------------------------\n   ----------------------------\n[-] "
        f"Version : v{__version__}")
    shibbot = Shibbot(test_mode=True)
    shibbot.run()
