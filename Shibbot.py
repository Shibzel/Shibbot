"""Launcher file :O"""
import os
from dotenv import load_dotenv
import requests
import orjson

from src import Shibbot, __version__ as version
from src.utils import Logger
from src.constants import DATABASE_PATH, LOGS_PATH, CACHE_PATH


OPTIONAL_CHECKS = True
TEST_MODE = True


repo_name = "Shibzel/Shibbot"

print(f"""
 ________________________________
|░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
|░░░█▀▀░█░█░▀█▀░█▀▄░█▀▄░█▀█░▀█▀░░|
|░░░▀▀█░█▀█░░█░░█▀▄░█▀▄░█░█░░█░░░|
|░░░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░░▀░░░|
|░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
 --------------------------------
   ----------- Version : v{version}""")

Logger.start()

### Doing some checks
if not os.path.exists("./.env"):
    Logger.error("Missing .env file.\n  -> Create a new one, copy the contents of .env.example and complete it.")
    exit()
# Loading .env
load_dotenv()

if not os.path.exists(DATABASE_PATH):
    open(DATABASE_PATH, "x")
    Logger.warn(f"Missing {DATABASE_PATH} file, creating one.")
folders_to_create = (LOGS_PATH, CACHE_PATH)
for dir in folders_to_create:
    if not os.path.exists(dir):
        os.makedirs(dir)

# Token
token = os.getenv("BOT_TOKEN") if not TEST_MODE else os.getenv("TEST_BOT_TOKEN")
if token == "":
    Logger.error("You forgot to set a token >:c\n  -> Go to your .env file to set one. You can get yours here : https://discord.com/developers/applications/")
    exit()

if OPTIONAL_CHECKS:
    # Version
    request = requests.get(f"https://api.github.com/repos/{repo_name}/tags")
    response = orjson.loads(request.text)
    if request.status_code == 200:
        last_version = response[0]["name"]
        if last_version == version:
            Logger.log("You're currently using the lastest version :O")
        else:
            version_listed = False
            for i in response:
                if i["name"] == version:
                    version_listed = True
                    Logger.warn(f"You're not using the latest version '{version}' < '{last_version}'.\n  -> Download the latest one here : https://github.com/{repo_name}/releases/")
                    break
            if not version_listed:
                Logger.warn("You're currently using a wip/unlisted version.")
    else:
        Logger.warn("Couldn't verify if the bot is up to date.")

    # Reddit
    if os.getenv("REDDIT_CLIENT_ID") in ("", None):
        Logger.error("Missing Reddit application client ID.\n  -> You can get your application's ID and secret here : https://www.reddit.com/prefs/apps/")
    if os.getenv("REDDIT_CLIENT_SECRET") in ("", None):
        Logger.error("Missing Reddit application client secret.")
    if os.getenv("REDDIT_USERNAME") in ("", None):
        Logger.error("Missing username of your Reddit account.")
    if os.getenv("REDDIT_PASSWORD") in ("", None):
        Logger.error("Missing password of your Reddit account.")

    # Lavalink
    if os.getenv("LAVALINK_HOST") in ("", None):
        Logger.error("Missing Lavalink server url/IP.\n  -> Self host your own Lavalink server or get a free one on the internet.")
    if os.getenv("LAVALINK_PORT") in ("", None):
        Logger.error("Missing Lavalink port.")
    if os.getenv("LAVALINK_PASSWORD") in ("", None):
        Logger.error("Missing Lavalink password.")

    # RapidAPI
    if os.getenv("RAPID_API_TOKEN") in ("", None):
        Logger.error("Missing RapidAPI token.\n  -> Get yours here : https://rapidapi.com/developer/new/")

    # Pterodactyl (for the hardware stats, optional)
    if os.getenv("USE_PTERO_API") in ('True', '1'):
        url = os.getenv("PTERO_PANEL_URL")
        if url == "":
            url = None
            Logger.error("Missing pterodactyl url.")
        elif str(url).endswith("/"):
            Logger.error("Your pterodactyl url mustn't end with '/'.")
        if os.getenv("PTERO_PANEL_TOKEN") in ("", None):
            Logger.error("Missing pterodactyl token."+("" if not url else f"  -> You can it here : {url}account/api/"))
        if os.getenv("PTERO_PANEL_SERVER_ID") in ("", None):
            Logger.error("Missing pterodactyl server ID."+("" if not url else f"  -> The ID is at the end of the server's link in the panel : {url}server/\033[93m8f61b2fb\033[00m"))

# Starting the bot
try:
    shibbot = Shibbot(
        test_mode=TEST_MODE,
        instance_owners=orjson.loads(os.getenv("BOT_OWNERS_IDS")),
        gc_clear=True
    )
    shibbot.run(token)
except Exception as e:
    Logger.error("Oops... Shibbot stopped ?", e)
    Logger.end()
