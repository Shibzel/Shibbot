![Banner](https://cdn.discordapp.com/attachments/797425043033686036/1051558257853988894/image.png)

<div align="center">
	<h1><b>Shibbot</b></h1>
    <img alt="Discord server" src="https://img.shields.io/discord/955507499778330625?color=5865F2&label=Discord&logo=Support&logoColor=white&style=for-the-badge">
	<img alt="Python version" src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge">
    <img alt="Lines of code" src="https://img.shields.io/tokei/lines/github/Shibzel/Shibbot?style=for-the-badge&color=orange">
    <img alt="Uptime" src="https://img.shields.io/uptimerobot/ratio/m792743228-711706b27e948a5682109c4e?style=for-the-badge">
	<h3>A feature-rich and modular Discord bot written in Python.</h3>
</div>

> **⚠️ This project is being rewrited, don't use it.**

## 🔮 Description & Motivation

Shibbot was the first project I *(\*Shibzel, the owner)* worked on to learn Python (which was a bad idea... don't start with that) then gradually evolved with my skills to what it is today : **a feature rich, open source Discord bot designed to be modular and accessible**.

**Its specificity** is to include several languages and plugins (which can be disabled with a command) without it being hard coded into the bot so that it can include external cogs and, use a file based database : SQLite 3 to not depend on external ressources that are not usually free. It can also use custom prefixed and `/slash` commands.

#### Right now it can :

- [ ] Help you with the moderation of your server (classic commands like tempban, normalize usernames, detect profanity...)
- [ ] Show you beautiful photos of shibas, cats and birds
- [ ] Get you the latest memes it scrobes on Reddit daily
- [ ] Offer you translation tools, articles on wikipedia and other utilities
- [ ] Play music in the voice channel you're in (classic)
- [ ] ~~Minecraft utilities (show the number of players into a server as a voice channel's name, ...)~~
- [x] Become sentient and threaten humanity

If you want to try it yourself on your server you can invite it by adding it on your own server by [clicking here](https://discord.com/api/oauth2/authorize?client_id=838922957547765801&permissions=8&scope=bot%20applications.commands) or join its server [here](https://discord.gg/TZNWfJmPwj).

## 🚀 Self-Hosting

Of course, a new instance of the bot can be hosted on your machine with your own modifications or "vanilla" but you must consider some things :
- Shibbot is not designed to be lightweight, you must provide him at least more than **64 MiB of RAM** otherwise it will not work or not proprely.
- Since it uses a file based portable database, **"hosts" like Heroku won't fit** because they wipe all the bot's files every 24 hours or less.
- It won't work out of the box, **don't forget to create a copy of `.env.exemple` named `.env` and reference the Discord token of the new instance and other credentials** that the bot needs. If you're using a host that use Pterodactyl you can set the utilisation of the Pterodactyl API to `True` so that the bot can know the usage of its hardware (optional).

Nevertheless, using our own hosted instance of the bot is also a higly recommended option if you just don't want to undergo all the issues that it is to host a Discord bot.

## 🤝 Contributing & Issues

**All feedbacks, bugs reports, forks and suggestions are welcome !** Do not hesistate to check out our [issues page](https://github.com/Shibzel/Shibbot/issues) or join our [Discord server](https://discord.gg/TZNWfJmPwj) for that.

It is maybe an useless reminder but a basic understanding of Python and the structure of the program is needed to pull commits into this repo. For that, we're working on a wiki that will arrive soon !

## 💼 Main contributors

- [Shibzel](https://github.com/Shibzel) : The owner and the one who worked the most on it (yet).
- [Cloudy_Paul](https://github.com/Cloudy-Paul) : For his incredible translation job.

Big thanks to all those listed [here](https://github.com/Shibzel/Shibbot/graphs/contributors) too !

## 📜 Requirements

- [Python 3.8+ (idealy 3.9 or 3.10)](https://www.python.org/downloads).
- Application credentials on [Reddit](https://www.reddit.com/prefs/apps) and [RapidAPI](https://rapidapi.com/developer/new).
- A [Lavalink Server](https://github.com/freyacodes/lavalink) you can host yourself or [or someone else's](https://www.google.com/search?q=free+lavalink+host).
- For the librairies see [`requirements.txt`](https://github.com/Shibzel/Shibbot/blob/main/requirements.txt).

Remember to fulfill the dependencies by running `python -m pip install -r requirements.txt` into your console before starting the bot.

## 💗 Credits

A big muah 😘 to everyone without whom this project would not be as great as it is !
- The community working on [Pycord](https://github.com/Pycord-Development/pycord/graphs/contributors), the Discord API wrapper used in Shibbot.
- The contributors of  [Lavalink](https://github.com/freyacodes/lavalink/graphs/contributors) (you know, the music server)
- [Covoxkid](https://twitter.com/covoxkid) for [Shibe.online](https://shibe.online) for the shibes, cats and birds images
- [Javier Aviles](https://github.com/javieraviles) for [Coronavirus-19-api](https://github.com/javieraviles/covidAPI) that fetches coronavirus stats
- The community of [RapidAPI](rapidapi.com) for the unofficial [Urban Dictionary API](https://rapidapi.com/community/api/urban-dictionary)



*Oh ? You reached the end...* <img src="https://cdn.discordapp.com/emojis/836308954601750578.webp?size=96" width="25px">
