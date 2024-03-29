try:
    import os
    import random
    from shutil import copyfile
    from platform import python_version, python_version_tuple
    try:
        import tomllib as toml
    except ModuleNotFoundError:
        import tomli as toml
    import requests
    import orjson

    from src import __version__
    from src.core import Shibbot, PterodactylShibbot
    from src.logging import Logger, ANSIEscape, LoggingLevel
except ModuleNotFoundError as exc:
    raise ImportError("An import error occurred."
        " Be sure you installed all the requirements modules or using a correct version of Python."
        "\nEntering this in your terminal could help :\n    python3 -m pip install -r requirements.txt") from exc


CONFIG_FILE_PATH = "./config.toml"
SPLASH_TEXT_FP = "./misc/splash_text.toml"


class MissingFile(Exception):
    """Raised when a necessary file is missing."""
    def __init__(self, fp: str = None, message: str | None = None):
        super().__init__(message or f"File '{fp}' is missing.")
    
class ConfigError(Exception):
    """Raised when there is a problem with the configuration file."""

class Syntax(ConfigError, TypeError):
    """Raised when there is a syntax problem or an type problem."""

class UncompletedOrMissing(ConfigError):
    """Raised when the a line in the config file is uncompleted or missing."""
    

def ascii_art(splash_text_fp: str, logger: Logger):
    """Shows a beautiful ascii art with a splash text."""
    try:
        with open(splash_text_fp, "rb") as f:
            splash_text = toml.load(f)["SplashText"]
    except (FileNotFoundError, toml.TOMLDecodeError) as err:
        logger.error("An error occurred while loading splash texts.", err)
        splash_text = ("placeholder",)
    print(f"""
            ᵛᵉʷʸ ᵖᵒʷᵉʳᶠᵘˡ
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⣀⣤⠀⣤⡄⡤⣤⢤⣀⡀
⠀⠀ʷᵒʷ⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⡐⠯⠹⣛⣋⢠⣭⣥⣭⣬⣬⣋⠃
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣘⠧⣓⢥⣶⣿⣿⣿⣷⣝⣿⣏⠰⣹⣿⠁
⠀⠀⠀⠀⠀⠀⡀⣶⣿⣿⢟⣥⣾⣏⡏⠫⠯⠊⢱⣿⣿⣮⢿⣿⣿⠃   ˢᵘᶜʰ ᵇᵒᵗ
⠀⠀⠀⠀⠀⠀⠘⢮⡻⣫⣾⣿⡳⠡⠀⢀⡀⠀⠹⣻⣿⣿⣎⣿⠃_____________________________
⠀⠀⠀⠀⠀⠀⠀⢠⠸⡞⣿⣿⡇⢘⡂⡀⠀⠀⠀⣿⣿⣿⡟░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
⠀⠀⢀⣠⣶⡶⠶⠶⠤⠙⣞⣿⣞⢄⡀⠀⠀⣀⢜⢞⡿⠋░░░█▀▀░█░█░▀█▀░█▀▄░█▀▄░█▀█░▀█▀░░|
⠀⢠⠿⢿⣿⣿⡿⠒⠀⠀⠈⢮⣻⣿⣾⣿⣿⣾⠵⠋ |░░░▀▀█░█▀█░░█░░█▀▄░█▀▄░█░█░░█░░░|
⠀⠀⣰⣿⣿⠋⢀⣀⣠⡄⠀⣀⠑⢝⠿⢝⣫⣵⡞  |░░░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░░▀░░░|
⠀⢠⣿⣿⣯⣶⣿⣿⣿⡇⣠⡟⡘⠀⢦⢿⣿⠟   |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
⠀⣾⣿⣿⣿⣿⠟⠁⣿⣿⡿⡡⠁⠀⠈⠋⠋     ---- • {ANSIEscape.bold + f'Version {__version__}' + ANSIEscape.endc} • ---------
⠼⠿⠿⠟⠋⠁⠀⠾⠛⠉⠈       > {ANSIEscape.italicize + random.choice(splash_text) + ANSIEscape.endc}
""")


def main(
    config_fp: str = CONFIG_FILE_PATH,
    config_example_fp: str = CONFIG_FILE_PATH + ".example",
    splash_text_dp: str = SPLASH_TEXT_FP,
    checks: bool = True,
    show_ascii: bool = True,
    *args, **_kwargs
):
    """Main function. Do some checks and then starts the bot."""
    cls = Shibbot

    # Verifies if the config file exists
    if not os.path.exists(config_fp):
        try:
            copyfile(config_example_fp, config_fp)
        except FileNotFoundError as exc:
            raise MissingFile(config_example_fp) from exc
        else:
            raise ConfigError(
                f"Please fulfill the requirements inside of the {config_fp} file.")
    # Loading config
    with open(config_fp, "rb") as toml_file:
        config: dict[str, dict | object] = toml.load(toml_file)
    settings = config["Settings"]
    console = settings["UseConsole"]
    debug = settings["DebugMode"]

    advanced = config["Advanced"]
    database = advanced["Database"]
    paths = advanced["Paths"]

    kwargs = {
        "debug": debug,
        "caching": settings["UseCache"],
        "minimal": settings["Minimal"],
        "allowed_cogs": settings["AllowedCogs"],
        "disabled_cogs": settings["DisabledCogs"],
        "database_fp": paths["Database"],
        "sqlite_cache_size": database["CacheSize"],
        "sqlite_cache_type": database["CacheType"],
    }

    logs_path = paths["Logs"]
    path_kwargs = {
        "extensions_path": paths["Extensions"],
        "cache_path": paths["Cache"],
        "temp_cache_path": paths["TemporaryCache"]
    }
    for path in path_kwargs.values():
        if not os.path.exists(path):
            os.makedirs(path)

    kwargs.update(path_kwargs)
    
    logger = Logger(
        path=logs_path,
        module=__name__,
        level=LoggingLevel.debug if debug else LoggingLevel.info,
    )
    kwargs["logger"] = logger
    
    if show_ascii:
        ascii_art(splash_text_dp, logger)

    # Discord
    discord = config["Discord"]
    token = discord["Token"]
    if not token:
        raise UncompletedOrMissing(
            "You forgot to set a token >:c"
            f" Go to your {CONFIG_FILE_PATH} file to set one."
            " You can get yours here : https://discord.com/developers/applications/"
        )
    instance_owners = []
    raw_ids = discord["OwnersID"]
    if raw_ids:
        try:
            for _id in raw_ids:
                assert len(str(_id)) >= 18
                instance_owners.append(int(_id))
        except (ValueError, AssertionError) as exc:
            raise Syntax(
                "Invalid Discord id(s)."
                " Make sure that the ids are integers (len >= 18) inside a list."
            ) from exc
    kwargs["instance_owners"] = instance_owners

    if checks:
        # Indicating Python version in debug logs
        py_ver = python_version()
        major, minor, _ = python_version_tuple()
        logger.debug(f"Running on Python {py_ver}.")
        if not 7 < int(minor) < 12 and int(major) != 3:
            logger.warn(
                f"Shibbot is not intended to run on version {py_ver} of Python.")

        # Code version
        repo_name = "Shibzel/Shibbot"
        try:
            request = requests.get(
                f"https://api.github.com/repos/{repo_name}/tags",
                timeout=5)
            response = orjson.loads(request.text)
            assert request.status_code == 200
            assert len(response) > 0
            last_version = response[0]["name"]
            if last_version == __version__:
                logger.log("You're currently using the latest version !")
            else:
                for release in response:
                    if release["name"] == __version__:
                        logger.warn(
                            f"You're not using the latest version '{__version__}' < '{last_version}'."
                            f" Download the latest one here : https://github.com/{repo_name}/releases/")
                        break
                else:
                    logger.warn("You're currently using a wip/unlisted version.")
        except (requests.RequestException, AssertionError) as err:
            logger.error("Couldn't verify if the bot is up to date.", err)

        # Pterodactyl (for the hardware stats, optional)
        pterodactyl = advanced["Pterodactyl"]
        if pterodactyl["UsePterodactylAPI"]:
            ptero_url = pterodactyl["URL"]
            if ptero_url in ("", "https://"):
                raise UncompletedOrMissing("Missing pterodactyl ptero_url.")
            if ptero_url.endswith("/"):
                raise Syntax("Your pterodactyl ptero_url mustn't end with '/'.")
            ptero_token = pterodactyl["Token"]
            if ptero_token in ("", "ptlc_"):
                raise UncompletedOrMissing(
                    f"Missing pterodactyl token. You can it here : {ptero_url}account/api/")
            ptero_server_id = pterodactyl["ServerID"]
            if ptero_server_id == "":
                raise UncompletedOrMissing(
                    "Missing pterodactyl server ID."
                    " The ID is at the end of the server's link in the panel :"
                    f" {ptero_url}server/" + ANSIEscape.underline + "1IdHere" + ANSIEscape.endc
                )
            cls = PterodactylShibbot
            parameters = {
                "ptero_url": ptero_url,
                "ptero_token": ptero_token,
                "ptero_server_id": ptero_server_id
            }
            kwargs.update(parameters)
        logger.debug("All checks done and settings loaded.")

    kwargs.update(_kwargs)

    # Starting the bot
    try:
        # Instancing Shibbot or PterodactylShibbot
        shibbot = cls(*args, **kwargs)
        shibbot.run(token, command_input=console)  # Running it
    except Exception as err:
        logger.critical("Oops... Shibbot stopped ?", err)
    
    logger.close()


if __name__ == "__main__":
    main()
