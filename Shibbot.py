import os
import requests
import orjson
import random
from shutil import copyfile
from platform import python_version, python_version_tuple
from dotenv import load_dotenv

from src import __version__ as version, __github__ as github
from src.core import Shibbot, PterodactylShibbot
from src.logging import Logger, PStyles


DEBUG = True
CONSOLE = True

class Missing(Exception): pass
class Syntax(Exception): pass

def ascii_art():
    """Shows a beautiful ascii art with a splash text."""
    splash_text = (PStyles.ERROR+"oUUuh scary error message"+PStyles.ENDC, PStyles.OKBLUE+"blue"+PStyles.ENDC, "goofy aah bot", " ", "a", "really cool ascii art huh?", "boTs havE riGhts ToO", "i love microplastics!", "microwaves be like: hmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm *ding*", "https://media.tenor.com/eyvN-SrFzkwAAAAC/nomoreamogus-amogus.gif", "https://www.youtube.com/watch?v=ZE4yIP2V2uQ", "*ping*", "created in 2021", "go watch Blade Runner 2049", "discord.com:443", "Around the World, Around the World 🎶", "god I love listening to CloudNone", "open source!", "I'm in your walls.", "Work of Shibzel!", "I know your exact location.", "Why are you even reading this", "Singlethreaded!", "I'm a teapot", "https://media.tenor.com/3qdiScnHBrEAAAAC/chicken.gif", ".　　 。　 ඞ 。 . 　　•", "STOP POSTING ABOUT AMONG US, I'M TIRED OF SEEING IT! My friends on TikTok send me memes, on Discord it's fucking memes, i was in a server, right? and ALL of the channels are just Among Us stuff. I-I showed my Champion underwear to my girlfriend, and the logo i flipped it and i said \"Hey babe, when the underwear sus HAHA ding ding ding ding ding ding ding *takes breath* ding ding ding\" I FUCKING LOOKED AT A TRASH CAN, I SAID \"THAT'S A BIT SUSSY\", I LOOKED AT MY PENIS, I THINK OF THE ASTRONAUT'S HELMET, AND I GO \"PENIS, more like peenSUS\" *takes breath* AAAAAAAAAAAAAAA", "Wooo, memes!", "https://media.tenor.com/pohmzAEOBAcAAAPso/speed-wheelchair.mp4", "a vewy gud bot", "amaznig!!!!", "holy cow!", "shibe going to space :O", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "Python Edition", "https://www.youtube.com/watch?v=JuEa6Hum0b4", "thanks for using shibbot!", github, "[put something here]", "computer compatible!", "random text!", "Water proof!", "69420 lines of code!", "https://media.tenor.com/GIYc9-gepHoAAAAd/shiba-inu.gif")
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
⠀⣾⣿⣿⣿⣿⠟⠁⣿⣿⡿⡡⠁⠀⠈⠋⠋     ---- • {PStyles.BOLD + f'Version {version}' + PStyles.ENDC} • ---------
⠼⠿⠿⠟⠋⠁⠀⠾⠛⠉⠈       > {PStyles.ITALICIZED + random.choice(splash_text) + PStyles.ENDC}
~~""")
     
def main():
    """Main function. Do some checks and then starts the bot."""
    cls = Shibbot
    kwargs = {"debug": DEBUG,}
    logger = Logger(__name__)
    logger.start()

    repo_name = github.replace("https://github.com/", "")
    try:
        # Indicating Python version in debug logs
        logger.debug(f"Running on Python {python_version()}.")
        if not 7 < int(python_version_tuple()[1]) < 12 and int(python_version_tuple()[0]) != 3: # If SOMEHOW you managed to run this script on something else than Python 3.x
            logger.error(f"Shibbot is not intended to run on version {python_version()} of Python.")

        # Verifies if the .env exists
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

        # Code version
        request = requests.get(f"https://api.github.com/repos/{repo_name}/tags")
        response = orjson.loads(request.text)
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
        logger.error("Hemmm... something went wrong :", e)
        logger.end()
        return e
    else:
        logger.debug("All checks done.")

    # Starting the bot
    try:
        # Instancing Shibbot or PterodactylShibbot with all the necessary kwargs
        shibbot = cls(**kwargs)
        shibbot.run(token, command_input=CONSOLE) # Running it
    except Exception as e:
        logger.error("Oops... Shibbot stopped ?", e)

    logger.end()
    
if __name__ == "__main__":
    ascii_art()
    main()
    exit() # Exiting because some threads that cannot be terminated can still be running