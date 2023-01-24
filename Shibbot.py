import os
from dotenv import load_dotenv
from requests import get
from orjson import loads
from platform import python_version, python_version_tuple
from shutil import copyfile

from src import __version__ as version, __github__ as github
from src.core import Shibbot, PterodactylShibbot
from src.logging import Logger, PStyles


DEBUG = True
CONSOLE = True

class Missing(Exception): pass
class Syntax(Exception): pass

def ascii_art():
    print(f"""
            ᵛᵉʷʸ ᵖᵒʷᵉʳᶠᵘˡ
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⣀⣤⠀⣤⡄⡤⣤⢤⣀⡀
    ⠀⠀ʷᵒʷ⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⡐⠯⠹⣛⣋⢠⣭⣥⣭⣬⣬⣋⠃
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣘⠧⣓⢥⣶⣿⣿⣿⣷⣝⣿⣏⠰⣹⣿⠁
    ⠀⠀⠀⠀⠀⠀⡀⣶⣿⣿⢟⣥⣾⣏⡏⠫⠯⠊⢱⣿⣿⣮⢿⣿⣿⠃
    ⠀⠀⠀⠀⠀⠀⠘⢮⡻⣫⣾⣿⡳⠡⠀⢀⡀⠀⠹⣻⣿⣿⣎⣿⠃
    ⠀⠀⠀⠀⠀⠀⠀⢠⠸⡞⣿⣿⡇⢘⡂⡀⠀⠀⠀⣿⣿⣿⡟
    ⠀⠀⢀⣠⣶⡶⠶⠶⠤⠙⣞⣿⣞⢄⡀⠀⠀⣀⢜⢞⡿⠋⠀⠀⠀ˢᵘᶜʰ ᵇᵒᵗ
    ⠀⢠⠿⢿⣿⣿⡿⠒⠀⠀⠈⢮⣻⣿⣾⣿⣿⣾⠵⠋
    ⠀⠀⣰⣿⣿⠋⢀⣀⣠⡄⠀⣀⠑⢝⠿⢝⣫⣵⡞
    ⠀⢠⣿⣿⣯⣶⣿⣿⣿⡇⣠⡟⡘⠀⢦⢿⣿⠟
    ⠀⣾⣿⣿⣿⣿⠟⠁⣿⣿⡿⡡⠁⠀⠈⠋⠋⠀⠀  - Shibbot⠀----
    ⠼⠿⠿⠟⠋⠁⠀⠾⠛⠉⠈         Version : v{version}
    """)

def main():
    cls = Shibbot
    kwargs = {"debug": DEBUG,}
    logger = Logger(__name__)
    logger.start()
    logger.set_debug_mode(DEBUG)

    ### Doing some checks
    repo_name = github.replace("https://github.com/", "")
    try:
        logger.debug(f"Running on Python {python_version()}.")
        if not 7 < int(python_version_tuple()[1]) < 12 and int(python_version_tuple()[0]) != 3: # If SOMEHOW you managed to run this script on something else than Python 3.x
            logger.error(f"Shibbot is not intended to run on version {python_version()} of Python.")

        if not os.path.exists("./.env"):
            try:
                copyfile("./.env.exemple", "./.env")
            except FileNotFoundError:
                raise Missing(f"There are missing files. To fix this you can re-download the code and try to run it again : https://github.com/{repo_name}/releases/")
            else:
                raise Missing("Please fulfill the requirements inside of the .env file.")
        # Loading .env
        load_dotenv()

        # Discord
        token = os.getenv("BOT_TOKEN")
        if token == "":
            raise Missing("You forgot to set a token >:c Go to your .env file to set one. You can get yours here : https://discord.com/developers/applications/")
        instance_owners = []
        raw_ids = os.getenv("BOT_OWNERS_ID")
        if raw_ids != "":
            try:
                for _id in raw_ids.split(" "):
                    assert len(_id) >= 18
                    instance_owners.append(int(_id))
            except (ValueError, AssertionError):
                raise Syntax("Invalid Discord ids. Be sure that the ids are separated with spaces and intergers.")
        kwargs["instance_owners"] = instance_owners

        # Version
        request = get(f"https://api.github.com/repos/{repo_name}/tags")
        response = loads(request.text)
        if request.status_code == 200:
            last_version = response[0]["name"]
            if last_version == version:
                logger.log("You're currently using the lastest version, thank you !")
            else:
                for release in response:
                    if release["name"] == version:
                        logger.warn(f"You're not using the latest version '{version}' < '{last_version}'. Download the latest one here : https://github.com/{repo_name}/releases/")
                        break
                else:
                    logger.warn("You're currently using a wip/unlisted version.")
        else:
            logger.error("Couldn't verify if the bot is up to date.")

        # Lavalink
        if os.getenv("LAVALINK_HOST") in ("", None):
            raise Missing("Missing Lavalink server ptero_url/IP. Self host your own Lavalink server or get a free one on the internet.")
        ll_port = os.getenv("LAVALINK_PORT")
        if ll_port in ("", None):
            raise Missing("Missing Lavalink port.")
        else:
            try:
                int(ll_port)
            except ValueError:
                raise Syntax("The Lavalink port isn't valid.")
        if os.getenv("LAVALINK_PASSWORD") in ("", None):
            raise Missing("Missing Lavalink password.")

        # Pterodactyl (for the hardware stats, optional)
        if os.getenv("USE_PTERO_API").lower() in ('true', '1'):
            ptero_url = os.getenv("PTERO_PANEL_URL")
            if ptero_url == "":
                raise Missing("Missing pterodactyl ptero_url.")
            elif ptero_url.endswith("/"):
                raise Syntax("Your pterodactyl ptero_url mustn't end with '/'.")
            ptero_token=os.getenv("PTERO_PANEL_TOKEN")
            if ptero_token in ("", None):
                raise Missing("Missing pterodactyl token." + ("" if not ptero_url else f" You can it here : {ptero_url}account/api/"))
            ptero_server_id = os.getenv("PTERO_PANEL_SERVER_ID")
            if ptero_server_id in ("", None):
                raise Missing("Missing pterodactyl server ID." + ("" if not ptero_url else f" The ID is at the end of the server's link in the panel : {ptero_url}server/" + \
                            PStyles.UNDERLINE + "8f61b2fb" + PStyles.ENDC))
            cls = PterodactylShibbot
            kwargs.update({"ptero_url": ptero_url, "ptero_token": ptero_token, "ptero_server_id": ptero_server_id,})
    except Exception as e:
        logger.error("Eh, something went wrong :", e)
        logger.end()
        return e
    else:
        logger.debug("All checks done.")

    # Starting the bot
    try:
        shibbot = cls(**kwargs)
        shibbot.run(token, command_input=CONSOLE)
    except Exception as e:
        logger.error("Oops... Shibbot stopped ?", e)

    logger.end()
    
if __name__ == "__main__":
    ascii_art()
    main()
    exit()