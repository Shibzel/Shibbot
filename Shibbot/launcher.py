"""Starts the bot with a beautiful ASCII art."""
from bot import Shibbot

if __name__ == "__main__":
    shibbot = Shibbot(test_mode=True)
    print(
        f" ________________________________\n|░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|\n|░░░█▀▀░█░█░▀█▀░█▀▄░█▀▄░█▀█░▀█▀░░|\n"
        f"|░░░▀▀█░█▀█░░█░░█▀▄░█▀▄░█░█░░█░░░|\n|░░░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░░▀░░░|\n"
        f"|░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|\n --------------------------------\n   ----------------------------\n[-] "
        f"Version : v{shibbot.version}")
    shibbot.run()
