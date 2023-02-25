import requests
import orjson
import random
from os import path
from shutil import copyfile
from platform import python_version, python_version_tuple
try:
    import tomllib as toml
except ModuleNotFoundError:
    import tomli as toml

from src import __version__ as version, __github__ as github
from src.core import Shibbot, PterodactylShibbot
from src.logging import Logger, PStyles


CONFIG_FILE_PATH = "./config.toml"
CONFIG_FP_EXEMPLE = CONFIG_FILE_PATH + ".exemple"

class Missing(Exception): pass
class Syntax(Exception): pass

def ascii_art():
    """Shows a beautiful ascii art with a splash text."""
    splash_text = (PStyles.ERROR+"oUUuh scary red message"+PStyles.ENDC, PStyles.OKBLUE+"blue"+PStyles.ENDC, "goofy aah bot", " ", "a", "really cool ascii art huh?", "boTs havE riGhts ToO", "i love microplastics!", "microwaves be like: hmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm *ding*", "https://media.tenor.com/eyvN-SrFzkwAAAAC/nomoreamogus-amogus.gif", "https://www.youtube.com/watch?v=ZE4yIP2V2uQ", "*ping*", "created in 2021", "go watch Blade Runner 2049", "discord.com:443", "Around the World, Around the World 🎶", "god I love listening to CloudNone", "open source!", "I'm in your walls.", "Work of Shibzel!", "I know your exact location.", "Why are you even reading this", "Singlethreaded!", "I'm a teapot", "https://media.tenor.com/3qdiScnHBrEAAAAC/chicken.gif", ".　　 。　 ඞ 。 . 　　•", "STOP POSTING ABOUT AMONG US, I'M TIRED OF SEEING IT! My friends on TikTok send me memes, on Discord it's fucking memes, i was in a server, right? and ALL of the channels are just Among Us stuff. I-I showed my Champion underwear to my girlfriend, and the logo i flipped it and i said \"Hey babe, when the underwear sus HAHA ding ding ding ding ding ding ding *takes breath* ding ding ding\" I FUCKING LOOKED AT A TRASH CAN, I SAID \"THAT'S A BIT SUSSY\", I LOOKED AT MY PENIS, I THINK OF THE ASTRONAUT'S HELMET, AND I GO \"PENIS, more like peenSUS\" *takes breath* AAAAAAAAAAAAAAA", "Wooo, memes!", "https://media.tenor.com/pohmzAEOBAcAAAPso/speed-wheelchair.mp4", "a vewy gud bot", "amaznig!!!!", "holy cow!", "shibe going to space :O", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "Python Edition", "https://www.youtube.com/watch?v=JuEa6Hum0b4", "thanks for using shibbot!", github, "[put something here]", "computer compatible!", "random text!", "Water proof!", "69420 lines of code!", "https://media.tenor.com/GIYc9-gepHoAAAAd/shiba-inu.gif")
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
    logger = Logger(__name__)
    logger.start()

    repo_name = github.replace("https://github.com/", "")
    try:
        # Indicating Python version in debug logs
        logger.debug(f"Running on Python {python_version()}.")
        if not 7 < int(python_version_tuple()[1]) < 12 and int(python_version_tuple()[0]) != 3: 
            # If SOMEHOW you managed to run this script on something else than Python 3.x
            logger.error(f"Shibbot is not intended to run on version {python_version()} of Python.")

        # Verifies if the config file exists
        if not path.exists(CONFIG_FILE_PATH):
            try:
                copyfile(CONFIG_FP_EXEMPLE, CONFIG_FILE_PATH)
            except FileNotFoundError:
                raise Missing(f"There are missing files. To fix this you can re-download the code and try to run it again : https://github.com/{repo_name}/releases/")
            else:
                raise Missing(f"Please fulfill the requirements inside of the {CONFIG_FILE_PATH} file.")
        # Loading config
        with open(CONFIG_FILE_PATH, "rb") as tf:
            config: dict = toml.load(tf)
        settings = config["Settings"]
        
        # Setting up debug mode
        debug = settings["DebugMode"]
        kwargs = {"debug": debug}     

        # Discord
        discord = config["Discord"]
        token = discord["Token"]
        if token == "":
            raise Missing(f"You forgot to set a token >:c Go to your {CONFIG_FILE_PATH} file to set one. You can get yours here : https://discord.com/developers/applications/")
        instance_owners = []
        raw_ids = discord["Owners"]
        if raw_ids != []:
            try:
                for _id in raw_ids:
                    assert len(_id) >= 18
                    instance_owners.append(int(_id))
            except (ValueError, AssertionError):
                raise Syntax("Invalid Discord ids. Make sure that the ids are intergers inside a array (list).")
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
        lavalink = config["Lavalink"]
        if lavalink["UseLavalink"]:
            if lavalink["IP"] in ("", "127.0.0.1"):
                raise Missing("Missing Lavalink server url/IP. Self host your own Lavalink server or get a free one on the internet.")
            ll_port = lavalink["Port"]
            if isinstance(ll_port, int):
                raise Syntax("The Lavalink port isn't valid.")
            if lavalink["Password"] == "":
                raise Missing("Missing Lavalink password.")

        # Pterodactyl (for the hardware stats, optional)
        pterodactyl = config["Pterodactyl"]
        if pterodactyl["UsePterodactylAPI"]:
            ptero_url = pterodactyl["URL"]
            if ptero_url in ("", "https://"):
                raise Missing("Missing pterodactyl ptero_url.")
            elif ptero_url.endswith("/"):
                raise Syntax("Your pterodactyl ptero_url mustn't end with '/'.")
            ptero_token = pterodactyl["Token"]
            if ptero_token in ("", "ptlc_"):
                raise Missing(f"Missing pterodactyl token. You can it here : {ptero_url}account/api/")
            ptero_server_id = pterodactyl["ServerID"]
            if ptero_server_id == "":
                raise Missing(f"Missing pterodactyl server ID. The ID is at the end of the server's link in the panel : {ptero_url}server/" + \
                              PStyles.UNDERLINE + "1IdHere" + PStyles.ENDC)
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
        shibbot.run(token, command_input=settings["UseConsole"]) # Running it
    except Exception as e:
        logger.error("Oops... Shibbot stopped ?", e)

    logger.end()
    
if __name__ == "__main__":
    ascii_art()
    main()
    exit() # Exiting because some threads that cannot be terminated can still be running