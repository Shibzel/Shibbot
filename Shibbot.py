import os
from dotenv import load_dotenv
import requests
import orjson

from src import Shibbot, PterodactylShibbot, __version__ as version
from src.utils import Logger
from src.constants import DATABASE_FILE_PATH, LOGS_PATH, CACHE_PATH


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

cls = Shibbot
class Missing(Exception): pass
class Syntax(Exception): pass

Logger.start()
### Doing some checks
try:
    if not os.path.exists("./.env"):
        raise Missing("Missing .env file. Create a new one, copy the contents of .env.example and complete it.")
    # Loading .env
    load_dotenv()

    if not os.path.exists(DATABASE_FILE_PATH):
        open(DATABASE_FILE_PATH, "x")
        Logger.warn(f"Missing {DATABASE_FILE_PATH} file, creating one.")
    folders_to_create = (LOGS_PATH, CACHE_PATH)
    for dir in folders_to_create:
        if not os.path.exists(dir):
            os.makedirs(dir)

    # Discord
    token = os.getenv("BOT_TOKEN")
    if token == "":
        raise Missing("You forgot to set a token >:c Go to your .env file to set one. You can get yours here : https://discord.com/developers/applications/")
    instance_owners = []
    raw_ids = os.getenv("BOT_OWNERS_ID")
    if raw_ids != "":
        try:
            for _id in raw_ids.split(" "):
                assert len(_id) == 18
                instance_owners.append(int(_id))
        except (ValueError, AssertionError):
            raise Syntax("Invalid Discord ids. Be sure that the ids are separated with spaces and intergers.")

    repo_name = "Shibzel/Shibbot"
    # Version
    request = requests.get(f"https://api.github.com/repos/{repo_name}/tags")
    response = orjson.loads(request.text)
    if request.status_code == 200:
        last_version = response[0]["name"]
        if last_version == version:
            Logger.log("You're currently using the lastest version, thank you !")
        else:
            version_listed = False
            for i in response:
                if i["name"] == version:
                    version_listed = True
                    Logger.warn(f"You're not using the latest version '{version}' < '{last_version}'. Download the latest one here : https://github.com/{repo_name}/releases/")
                    break
            if not version_listed:
                Logger.warn("You're currently using a wip/unlisted version.")
    else:
        Logger.warn("Couldn't verify if the bot is up to date.")

    # Reddit
    if os.getenv("REDDIT_CLIENT_ID") in ("", None):
        raise Missing("Missing Reddit application client ID. You can get your application's ID and secret here : https://www.reddit.com/prefs/apps/")
    if os.getenv("REDDIT_CLIENT_SECRET") in ("", None):
        raise Missing("Missing Reddit application client secret.")
    if os.getenv("REDDIT_USERNAME") in ("", None):
        raise Missing("Missing username of your Reddit account.")
    if os.getenv("REDDIT_PASSWORD") in ("", None):
        raise Missing("Missing password of your Reddit account.")

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

    # RapidAPI
    if os.getenv("RAPID_API_TOKEN") in ("", None):
        raise Missing("Missing RapidAPI token. Get yours here : https://rapidapi.com/developer/new/")

    # Pterodactyl (for the hardware stats, optional)
    if os.getenv("USE_PTERO_API") in ('True', '1'):
        ptero_url = os.getenv("PTERO_PANEL_URL")
        if ptero_url == "":
            raise Missing("Missing pterodactyl ptero_url.")
        elif ptero_url.endswith("/"):
            raise Syntax("Your pterodactyl ptero_url mustn't end with '/'.")
        ptero_token=os.getenv("PTERO_PANEL_TOKEN")
        if ptero_token in ("", None):
            raise Missing("Missing pterodactyl token."+("" if not ptero_url else f" You can it here : {ptero_url}account/api/"))
        ptero_server_id = os.getenv("PTERO_PANEL_SERVER_ID")
        if ptero_server_id in ("", None):
            raise Missing("Missing pterodactyl server ID."+("" if not ptero_url else f" The ID is at the end of the server's link in the panel : {ptero_url}server/\033[93m8f61b2fb\033[00m"))
        cls = PterodactylShibbot
except (Missing, Syntax) as e:
    Logger.error("Eh, your forgot something.", e)
    exit()

# Starting the bot
try:
    shibbot = cls(
        test_mode=True, instance_owners=instance_owners,
        gc_clear=True,
        ptero_url=ptero_url, ptero_token=ptero_token, ptero_server_id=ptero_server_id,
    )
    shibbot.run(token=token, command_input=True)
except Exception as e:
    Logger.error("Oops... Shibbot stopped ?", e)
    Logger.end()
