![Banner](https://cdn.discordapp.com/attachments/797425043033686036/1051558257853988894/image.png)

<div align="center">
	<h1><b>Shibbot</b></h1>
	<h3>A feature-rich and modular Discord bot written in Python.</h3>
	<img alt="Python version" src="https://img.shields.io/badge/Python-3.8 | 3.9 | 3.10 | 3.11-blue?style=for-the-badge&logo=Python&logoColor=white" href="https://www.python.org/downloads">
    <img alt="Release" src="https://img.shields.io/github/v/release/Shibzel/Shibbot?include_prereleases&label=Latest%20Release&logo=github&sort=semver&style=for-the-badge&logoColor=white&color=red" href="https://github.com/Shibzel/Shibbot/releases/latest">
    <img alt="Lines of code" src="https://img.shields.io/tokei/lines/github/Shibzel/Shibbot?style=for-the-badge&color=orange">
    <img alt="Discord server" src="https://img.shields.io/discord/955507499778330625?color=5865F2&label=Server&logo=Discord&logoColor=white&style=for-the-badge" href="https://discord.gg/TZNWfJmPwj">
    <img alt="Uptime" src="https://img.shields.io/uptimerobot/ratio/m792743228-711706b27e948a5682109c4e?style=for-the-badge">
</div>
<p align="center">
    <a href="#-description--motivation">Description</a>
    |
    <a href="#-self-hosting">Hosting</a>
    |
    <a href="#-contributing--issues">Contributing</a>
    |
    <a href="https://github.com/Shibzel/Shibbot/blob/main/LICENSE">Liscense</a>
</p>

> # **⚠️ This project is being rewrited, don't use it.**

## 🔮 Description & Motivation

Shibbot was the first project I *(\*Shibzel, the owner)* worked on to learn Python (which was a bad idea... don't start with that) then gradually evolved with my skills to what it is today : **a feature rich, open source Discord bot designed to be modular and accessible**.

**Its specificity** is to include several languages and plugins (which can be disabled with a command) without it being hard coded into the bot so that it can include external cogs and; use a file based database : SQLite 3 to not depend on external ressources that are not usually free. It can also use custom prefixed and `/slash` commands.

#### Right now it can :

- [ ] Help you with the moderation of your server with all the classic commands like ban, tempmute, warn...
- [ ] Additional specific commands completing the classic moderation commands ("normalize" usernames, clear a user's messages, massban ...)
- [ ] Automod (dangerous links and profanity detection...)
- [x] Show you beautiful photos of shibas, capybaras, cats and birds
- [x] Show you memes collected on Reddit.
- [x] Offer you translation tools, articles on wikipedia and other utilities
- [ ] Play music in the voice channel you're in (classic)
- [x] Become sentient and threaten humanity
- [x] Have more functionality thanks to the addition of extensions (external cogs).

If you want to try it yourself on your server you can invite it by adding it on your own server by [clicking here](https://discord.com/api/oauth2/authorize?client_id=838922957547765801&permissions=8&scope=bot%20applications.commands) or join its server [here](https://discord.gg/TZNWfJmPwj).

## 🚀 Self-Hosting

Of course, a new instance of the bot can be hosted on your machine with your own modifications or "vanilla" but you must consider some things :
- Shibbot is not designed to be lightweight, you must provide him at least more than **64 MiB of RAM** otherwise it will not work or not proprely.
- Since it uses a file based portable database, **"hosts" like Heroku won't fit** because they wipe all the bot's files every 24 hours or less.
- It won't work out of the box, **don't forget to create a copy of [`config.toml.exemple`](/config.toml.exemple) named `config.toml` and reference the Discord token of the new instance and other credentials** that the bot needs. If you're using a host that use [Pterodactyl](https://pterodactyl.io/) you can set the utilisation of the Pterodactyl API to `True` so that the bot can know the usage of its hardware (optional).

Nevertheless, using our own hosted instance of the bot is also a higly recommended option if you just don't want to undergo all the issues that it is to host a Discord bot.

## 📜 Requirements

- [Python 3.8 to 3.11](https://www.python.org/downloads).
- A [Lavalink Server](https://github.com/freyacodes/lavalink) you can host yourself or [someone else's](https://www.google.com/search?q=free+lavalink+host).
- For the librairies see [`requirements.txt`](/requirements.txt).

Remember to fulfill the dependencies by running `python -m pip install -r requirements.txt` into your console before starting the bot.

## 🤝 Contributing & Issues

**All feedbacks, bugs reports, forks and suggestions are welcome !** Do not hesistate to check out our [issues page](https://github.com/Shibzel/Shibbot/issues) or join our [Discord server](https://discord.gg/TZNWfJmPwj) for that.

It is maybe an useless reminder but a basic understanding of Python and the structure of the program is needed to pull commits into this repo. For that, we're working on a wiki that will arrive soon !

## 💼 Main contributors

- [Shibzel](https://github.com/Shibzel) : The owner and the one who worked the most on it (yet).
- [Cloudy_Paul](https://github.com/Cloudy-Paul) : For his incredible translation job.

Big thanks to all those listed [here](https://github.com/Shibzel/Shibbot/graphs/contributors) too !

## 💗 Credits

A big muah 😘 to everyone without whom this project would not be as great as it is ! To :
- The community working on [Pycord](https://github.com/Pycord-Development/pycord/graphs/contributors), the Discord API wrapper used in Shibbot.
- The contributor(s) of  [Lavalink](https://github.com/freyacodes/lavalink/graphs/contributors) (you know, the music server), [shibe.online](https://shibe.online), [themealdb.com](https://www.themealdb.com), [meme-api.com](https://github.com/D3vd/Meme_Api) and [capy.lol](https://github.com/Looskie/capybara-api).

*Oh ? You reached the end...* <img src="https://cdn.discordapp.com/emojis/836308954601750578.webp?size=96" width="25px">
