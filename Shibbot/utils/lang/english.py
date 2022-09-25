"""Surely a wrong way to do this but watever."""


class English:
    def __init__(self):
        self.DEFAULT_REQUESTED_FOOTER = "Requested by {author}."

        # ping.py cog
        self.ping = {
            "embed": {
                "title": "🏓 Pong !",
                "description": "Shibbot's latency : `{ping}ms`\nMachine load : `CPU: {cpu}%` `RAM: {ram}%`"
            },
            "buttons": {
                "status": "Status Page"
            }
        }

        # help.py cog
        self.get_invitation = {
            "embed": {
                "title": "Invitation",
                "description": "Use the buttons below me to hop into. Thanks if you're inviting Shibbot !",
                "footer": "Actual footage of a happy doggo using Shibbot. | Shibbot • v{version}",
            },
            "buttons": {
                "bot_invite": "Invite me !",
                "support": "Support server"
            }
        }
        self.bot_info = {
            "embed": {
                "title": "About Shibbot",
                "fields": [
                    {
                        "name": "Description",
                        "value": "Shibbot is a multipurpose bot present on `{n_servers}` servers and written in Python by JeanTheShiba ([dsc.bio](https://dsc.bio/jls), [github](https://github.com/JeanLeShiba)). The goal is to provide a funny, good and modular bot for people managing Discord servers and the members themselves with moderation, fun plugins, utilities... It is still in beta so you can sometimes encounter bugs, if so contact me or join the support server."
                    },
                    {
                        "name": "Specs",
                        "value": "The bot is currently running on :\n🐍 Python version : `{python_version}`\n⚡ Pycord version : `{pycord_version}`\n❤ Cores : `{n_threads} thread(s)`\n📏 RAM : `{ram_usage}/{n_ram}MB`\n🖥 Hosted in : `{place}`"
                    },
                    {
                        "name": "Support the project",
                        "value": "This project was was done with no aim to get money so please consider doing [a Paypal donation]({donation_link}) (thank you). If you want to contribute to the project by reporting a bug or improving it, go to [the Github page](https://github.com/JeanLeShiba/Shibbot) or contact me in private message/the support server."
                    }
                ]
            }
        }
        self.show_help = {
            "embed": {
                "title": "__**Shibbot Help!**__",
                "description": "**Hi 👋 ! I'm Shibbot**, a multipurpose discord bot that can do stuff like moderation, searches on wikipedia, send memes, etc... Want to learn more about me ? Use `botinfo`, wow.",
                "fields": [
                    {
                        "name": "Commands to get started :",
                        "value": "- `plugins` : To enable or disable the bot's plugins (use it if it's the first time for the bot on this server).\n- `lang` : Changes the language.\n- `prefix` : For a custom prefix on this server."
                    },
                    {
                        "name": "What's new ?",
                        "value": "🇫🇷 French language support\nPossibility to kick or ban multiple members in one command\nNormalize a member's username with `username`\nAdded birds and cats"
                    },
                    {
                        "name": "Get help :",
                        "value": "The current prefix is `{prefix}`. To get the list of my commands on a category, click on the bar bellow and select one of the options to jump in ⬇."
                    }
                ],
                "footer": "Shibbot v{version} | Legend: []: required • <> : optional • ⚠ Not available/working yet"
            },
            "select": {
                "placeholder": "Select a category here :",
                "info": {
                    "label": "Bot's commands",
                    "description": "Learn more about the bot and configure it on your server."
                },
                "mod": {
                    "label": "Moderation",
                    "description": "Allows you to moderate your members with both basic and advanced functions."
                },
                "fun": {
                    "label": "Entertainement",
                    "description": "Fun commands. Yay."
                },
                "tools": {
                    "label": "Tools",
                    "description": "Useful tools to use directly in a channel."
                },
            },
            "buttons": {
                "invite": "Invite me!",
                "support": "Support Server",
                "donate": "Donate"
            },
            "info": {
                "description": "**Info & Config :** Learn more about the bot and configure it on your server.",
                "fields": [
                    {
                        "name": "Commands",
                        "value": """
- `help`: Shows this command
- `invite`: Gives a link to invite the bot to your own server or to join the bot's server
- `ping`: Shows Shibbot's ping
- `plugins` : To enable or disable the bot's plugins (use it if it's the first time for the bot on this server)
- `lang` : Changes the language
- `prefix [prefix]` : For a custom prefix on this server
- `avatar <user>` : Shows the avatar of an user
- `uinfo [user]` : Shows some infos about the specified user
- `serverinfo` : Shows some info about the server you are currently in
"""
                    }
                ]
            },
            "mod": {
                "description": "**Moderation :** Allows you to moderate your members with both basic and advanced functions.",
                "fields": [
                    {
                        "name": "Classic commands",
                        "value": """
- `logs [channel]` : Defines or changes the logs channel for moderation
- `clear [amount] <user>` : Clears up to 100 messages in a channel
- `warn [member] <reason>` : Warns a member
- `clearwarns [user]` : Clears all the warnings of an user
- `mute [member] <reason>` : Mutes a member
- `unmute [member] <reason>` : Unmutes a member
- `kick [member] <reason>` : Kicks a member
- `ban [user] <reason>` : Bans a member
- `unban [user] <reason>` : Remove an user from the ban list"""
                    },
                    {
                        "name": "Temporary commands",
                        "value": """
- `tempmute [member] [duration] <reason>` : Mutes a member for a specified duration
- `tempban [member] [duration] <reason>` : Bans a member for a specified duration
"""
                    },
                    {
                        "name": "Specific/advanced commands",
                        "value": """
- `normalize [member]` : Cleans a member's nickname
- `nuke` : KADABOOMs a maximum 1000 messages in a channel
- `softban [member] <reason>` : Kicks a member from the server, deletes all messages last 24 hours old and invites the user back. Handy if someone got hacked
- `multikick [members separated by a space]` : Kicks multiple members in one command
- `multiban [members separated by a space]` : Same as `multikick` but for bans"""
                    },
                    {
                        "name": "Info commands",
                        "value": """
- `warnings [user]` : Shows the warnings of an user
⚠ - `perms [member]` : Shows all the permissions of a member
⚠ - `roles [member]` : Shows all the roles of a member
"""
                    }
                ]
            },
            "fun": {
                "description": "**Entertainement :** Fun commands. Yay.",
                "fields": [
                    {
                        "name": "Commands",
                        "value": """
- `meme` : Gives random memes stolen from Reddit
- `nsfwmeme` : Same as `meme` but only with nsfw memes
- `shiba` : Shows random shibe
- `bird` : Same as shibe
- `cat` : Same as cat
- `piss` : *piss*
- `twitter` : ratio + L + fatherless + maidenless
- `randnum [a] <b>` : Gives a random number between `a` and `b` or `0` and `a` if `b` is not precised"""
                    }
                ]
            },
            "tools": {
                "description": "**Tools :** Useful tools to use directly in a channel.",
                "fields": [
                    {
                        "name": "Commands",
                        "value": """
- `wikipedia [search]` : Searches an article on wikipedia (in beta, doesn't work well)
- `translate [language] [sentence]` : Translates sentence into a specified language
- `covid [country]` : Searches covid cases on a country
- `urbandict [word]` : Gives the definition of a word found on Urban Dictionary"""
                    }
                ]
            }
        }

        # events.py cog
        self.on_command_error = {
            "CommandOnCooldown": {
                "description": "Wait, wait ! This command is on cooldown, you cannot use it until this message disappears (`{secs} second(s)`)."
            },
            "PrivateMessageOnly": {
                "description": "This command is dm only."
            },
            "NoPrivateMessage": {
                "description": "This command is guild only."
            },
            "NotOwner": {
                "description": "You're not my owner, you can't use this command."
            },
            "UserNotFound": {
                "description": "Couldn't find that user."
            },
            "ChannelNotFound": {
                "description": "Couldn't find that channel."
            },
            "NSFWChannelRequired": {
                "description": "This channel {channel} isn't for NSFW content ! Kids might be shocked."
            },
            "MissingPermissions": {
                "description": "You can't do that. You're missing {permissions} permission(s) to run this command.",
                "and": "and"
            },
            "BotMissingPermissions": {
                "description": "It seems that the bot is missing permissions, if you can manage roles putting Shibbot's role higher may be a solution or you're asking to do something impossible."
            },
            "BadArgument": {
                "description": "Sorry, bad argument(s). Use the `help` command to get the list of commands."
            },
            "CommandError": {
                "description": "Something went wrong, I couldn't do that.",
                "footer": "If the problem persists, contact the owner of the bot : {owner}.",
                "dissmiss": "dissmiss"
            }
        }

        # tools.py cog
        self.urbain_dictionary = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a word to search on Urban Dictionary !\nUsage : `udict [word]`"
                }
            },
            "embed": {
                "fields": [
                    {
                        "name": "Definition of {word} by '{author}'"
                    },
                    {
                        "name": "Example"
                    }
                ]
            },
            "buttons": {
                "next": "Next Definition",
                "previous": "Previous"
            }
        }
        self.get_covid_stats = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a country or `world` to get global data !\nUsage : `covid [country]`"
                }
            },
            "loading_embed": {
                "title": "Wait a second...",
                "description": "I'm fetching data..."
            },
            "embed": {
                "title": "COVID-19 status of {country}",
                "description": "Here are the stats :",
                "fields": [
                    {
                        "name": "Cases"
                    },
                    {
                        "name": "Total Cases"
                    },
                    {
                        "name": "Deaths"
                    },
                    {
                        "name": "Total Deaths"
                    },
                    {
                        "name": "Recovered"
                    },
                    {
                        "name": "Active"
                    },
                    {
                        "name": "Critical"
                    },
                    {
                        "name": "Cases per 1/Million"
                    },
                    {
                        "name": "Deaths per 1/Million"
                    },
                    {
                        "name": "Total Tests"
                    },
                    {
                        "name": "Tests per 1/Million"
                    },
                    {
                        "name": "Pay attention :",
                        "value": "The information given here may not be live and therefore inaccurate. Source : [www.worldometers.info](http://www.worldometers.info)."
                    }
                ]
            }
        }
        self.translate_text = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a language and a text to tranlate !\nUsage : `trans [language] [sentence]`"
                },
                "bad_args": {
                    "title": "Try again !",
                    "description": "No support for the provided language."
                },
                "unavalaible": {
                    "title": "Unavailable...",
                    "description": "Service unavailable, try again later."
                }
            },
            "embed": {
                "title": "Translate",
                "fields": [
                    {
                        "name": "Original Text :"
                    },
                    {
                        "name": "Translated :"
                    }
                ]
            }
        }
        self.search_on_wikipedia = {
            "checks": {
                "missing_args": {
                    "description": "Gimme something to search !\nUsage : `wiki [article]`"
                },
                "not_found": {
                    "description": "Couldn't find anything for '{article}', try again."
                }
            },
            "selection_embed": {
                "description": "Use the bar below to get the item you want ! (it won't bite)"
            },
            "select": {
                "placeholder": "Select an article here :"
            },
            "loading_embed": {
                "title": "Wait a second...",
                "description": "I'm fetching data... That can take a little second."
            }
        }

        # fun.py cog
        self.get_random_number = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a numbers or two !\nUsage : `randint [x] <y>`"

                }
            }
        }
        self.shibes_viewer = {
            "buttons": {
                "previous": "Previous one",
                "next": "Next Shibe"
            }
        }
        self.cats_viewer = {
            "buttons": {
                "previous": "Previous one",
                "next": "Next Cat"
            }
        }
        self.birds_viewer = {
            "buttons": {
                "previous": "Previous one",
                "next": "Next Birb"
            }
        }
        self.meme_viewer = {
            "buttons": {
                "previous": "Previous Meme",
                "next": "Next Meme"
            }
        }
        self.nsfw_meme_viewer = {
            "buttons": {
                "previous": "Previous Meme",
                "next": "Next Meme"
            }
        }

        # config.py cog
        self.enable_disable_plugins = {
            "embed": {
                "title": "Plugins",
                "description": "Use the bar bellow to select the plugins you want to disable or enable."
            },
            "options": {
                "mod": {
                    "label": "Moderation",
                    "description": "Allows you to moderate your members with both basic and advanced functions."
                },
                "fun": {
                    "label": "Fun",
                    "description": "Fun commands. Yay."
                },
                "tools": {
                    "label": "Tools",
                    "description": "Useful tools to use directly in a channel."
                },
                "placeholder": "Select plugins here :"
            },
            "content": "Done !"
        }
        self.change_prefix = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a prefix to change (must be lower than 8 caracters) !\nUsage : `prefix [prefix]`"

                },
                "length_exceeded": {
                    "title": "Oops...",
                    "description": "The prefix must have less than 8 characters !"

                }
            },
            "embed": {
                "title": "Done !",
                "description": "The prefix has successfully been updated to `{prefix}`."
            }
        }
        self.change_logs_channel = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a logs channel to define ! Usage : `logs [channel]`"

                }
            },
            "embed": {
                "title": "Done !",
                "description": "The logs channel has successfully been updated to {channel}."
            }
        }
        self.change_language = {
            "embed": {
                "title": "Language",
                "description": "Use the bar bellow to select a language to set."
            },
            "options": {
                "en": {
                    "label": "English"
                },
                "fr": {
                    "label": "French"
                },
                "placeholder": "Select a language here :"
            },
            "content": "Done !"
        }

        # mod.py cog
        self.log_on_member_remove = {
            "embed": {
                "action": "Kick",
                "description": "{member} (id : `{member_id}`) has been kicked by {mod}\nReason : {reason}."
            }
        }
        self.log_on_member_ban = {
            "embed": {
                "action": "Kick",
                "description": "{member} (id : `{member_id}`) has been banned by {mod}\nReason : {reason}."
            }
        }
        self.log_on_member_unban = {
            "embed": {
                "action": "Kick",
                "description": "{member} (id : `{member_id}`) is now unbanned."
            }
        }
        self.log_unmute = {
            "embed": {
                "action": "Unmute",
                "description": "{member} (id : `{member_id}`) has been unmuted."
            }
        }
        self.log_purge = {
            "embed": {
                "action": "Purge",
                "description": "{mod} purged {n_message} messages in {channel}."
            },
        }
        self.clear_messages = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a number of messages to clear and optionally an user !\nUsage : `clear [amount] <user>`"
                }
            },
            "member_clear": {
                "title": "Done !",
                "description": "Deleted `{n_messages}` messages of {member}.",
                "footer": "The messages older than 2 weeks cannot be deleted by the bot (Discord restrictions)."

            },
            "channel_clear": {
                "title": "Done !",
                "description": "Removed `{n_messages}` messages in this channel."
            }
        }
        self.nuke_channel = {
            "embed": {
                "title": "Ok, wait a second !",
                "description": "You're about to nuke this channel and **up to 1000 messages will be deleted**. Are you sure you wanna do this ?"
            },
            "buttons": {
                "no": "nah i'm good",
                "yes": "KADABOOOM"
            },
            "done": {
                "title": "Done !",
                "description": "Kadaboomed `{n_messages}` messages in this channel, that was very effective !"
            }
        }
        self.warn_member = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a member to warn !\nUsage : `warn [member] <reason>`"
                }
            },
            "embed": {
                "title": "Warned !",
                "description": "<a:verified:836312937332867072> You've warned {member}. They now have `{n_warns}` warn(s) !\nReason : {reason}"
            },
            "log": {
                "action": "Warn n°{n_warns}",
                "description": "{member} (id : `{member_id}`) has been warned by {mod}.\nReason : {reason}."
            },
            "pm": {
                "description": "You've been warned on **{guild}**.\nReason : {reason}."
            }
        }
        self.clear_user_warns = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a user with warns to clean !\nUsage : `clearwarns [member] <reason>`"
                }
            },
            "embed": {
                "title": "Infractions cleared !",
                "description": "All the infractions of {member} has been removed."
            },
            "log": {
                "action": "Warns clear",
                "description": "{mod} cleared all the warns of {member}.\nReason : {reason}."
            }
        }
        self.show_warnings = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a user to search !\nUsage : `warnings [member] <reason>`"
                }
            },
            "embed": {
                "title": "Infractions",
                "description": "Here's all the infractions of {member} (id : `{member_id}`) :",
                "fields": {
                    "no_infra": {
                        "name": "No infraction",
                        "value": "This user has not yet been warned (must be an angel... or the mods aren't doing their work, idk.)"
                    },
                    "warn": {
                        "name": "Warn n°{n_warn}",
                        "value": "Reason : {reason}\nBy {mod} on `{date}`"
                    }
                },
                "buttons": {
                    "previous": "Previous",
                    "next": "Next"
                }
            }
        }
        self.mute_member = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a member to mute !\nUsage: `mute[member] <reason>`"

                },
                "already_muted": {
                    "title": "Oops...",
                    "description": "This member is already muted !"
                }
            },
            "embed": {
                "title": "Muted !",
                "description": "Just muted {member}.\nReason : {reason}"
            },
            "log": {
                "action": "Mute",
                "description": "{member} (id : `{member_id}`) has been muted by {mod}.\nReason : {reason}."
            },
            "pm": {
                "description": "You've been muted on **{guild}**.\nReason : {reason}."
            }
        }
        self.tempmute_member = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a member to tempmute !\nUsage: `tmute [member] [duration] <reason>`"
                },
                "already_muted": {
                    "title": "Oops...",
                    "description": "This member is already muted !"
                }
            },
            "embed": {
                "title": "Muted !",
                "description": "{member} is now tempmuted for `{duration}`.\nReason : {reason}"
            },
            "log": {
                "action": "Tempmute",
                "description": "{member} (id : `{member_id}`) has been tempmuted by {mod} for `{duration}`.\nReason : {reason}."
            },
            "pm": {
                "description": "You've been tempmuted on **{guild}** for `{duration}`.\nReason : {reason}."
            }
        }
        self.unmute_member = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a member to unmute !\nUsage: `tmute [member]`"
                },
                "not_muted": {
                    "title": "Oops...",
                    "description": "This member is not muted !"
                }
            },
            "embed": {
                "title": "Muted !",
                "description": "{member} is now unmuted."
            },
            "pm": {
                "description": "You've been unmuted from **{guild}**."
            }
        }
        self.yeet_member = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a member to kick !\nUsage : `kick [member] <reason>`"
                }
            },
            "embed": {
                "title": "Kicked !",
                "description": "{member} has been yeeted out from the server.\nReason : {reason}"
            },
            "pm": {
                "description": "You've been kicked from **{guild}**.\nReason : {reason}"
            }
        }
        self.yeet_members = {
            "checks": {
                "missing_args": {
                    "description": "Gimme members to kick !\nUsage : `kick [members] <reason>`"
                }
            },
            "embed": {
                "title": "Multikcick command",
                "fields": [
                    {
                        "name": "Sucessful kick(s)"
                    },
                    {
                        "name": "Failed kick(s)"
                    }
                ]
            },
            "pm": {
                "description": "You've been kicked from **{guild}**."
            }
        }
        self.ban_user = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a user to ban !\nUsage : `ban [user] <reason>`"
                }
            },
            "embed": {
                "title": "Banned !",
                "description": "Banishing hammer sagged on {member}.\nReason : {reason}"
            },
            "pm": {
                "description": "You've been banned from **{guild}**.\nReason : {reason}"
            }
        }
        self.tempban_member = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a user to tempban !\nUsage: `tban [user] [duration] <reason>`"
                }
            },
            "embed": {
                "title": "Banned !",
                "description": "{member} is now tempbanned for `{duration}`.\nReason : {reason}"
            },
            "log": {
                "action": "Tempban",
                "description": "{member} (id : `{member_id}`) has been tempbanned by {mod} for `{duration}`.\nReason : {reason}."
            },
            "pm": {
                "description": "You've been tempbanned on **{guild}** for `{duration}`.\nReason : {reason}."
            }
        }
        self.softban_member = {
            "checks": {
                "missing_args": {
                    "description": "( ﾉ ﾟｰﾟ)ﾉ Gimme a member to soft-ban !\nUsage : `softban [member] <reason>`"
                }
            },
            "pm": {
                "description": "You've been soft-banned from **{guild}** for the following reason : '{reason}'.\nUse this link to come back : {invite}"
            },
            "embed": {
                "title": "Tempbanned !",
                "description": "{member} has been softbanned.\nReason : {reason}"
            },
            "log": {
                "action": "Softban",
                "description": "{member} (id : `{member_id}`) has been softbanned by {mod}.\nReason : {reason}."
            }
        }
        self.ban_members = {
            "checks": {
                "missing_args": {
                    "description": "Gimme members to ban !\nUsage : `mban [members] <reason>`"
                }
            },
            "embed": {
                "title": "Multiban command",
                "fields": [
                    {
                        "name": "Sucessful ban(s)"
                    },
                    {
                        "name": "Failed ban(s)"
                    }
                ]
            },
            "pm": {
                "description": "You've been banned from **{guild}**."
            }
        }
        self.unban_user = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a user to unban !\nUsage: `unban [user]`"
                }
            },
            "embed": {
                "title": "Muted !",
                "description": "{member} is now unbanned."
            },
            "pm": {
                "description": "You've been unbanned from **{guild}**."
            }
        }
        self.normalize_nickname = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a member with a nickname to normalize.\nUsage : `normalize [member]`."
                },
                "already_normal": {
                    "title": "Hm.",
                    "description": "`{nickname}` seems normal for me, nothing changed."
                }
            },
            "embed": {
                "title": "Normalized !",
                "description": "I cleaned {member} nickname."
            }
        }

        # misc.py cog
        self.show_avatar = {
            "embed": {
                "description": "{member}'s avatar :"
            }
        }
        self.get_guild_info = {
            "loading_embed": {
                "description": "Fetching..."
            },
            "embed": {
                "title": "Server Info",
                "description": "Some information about **{guild}** :",
                "fields": [
                    {
                        "name": "__Main information__",
                        "value": "**🔍 Name :** `{guild_name}`\n**🆔 ID :** `{guild_id}`\n**⏲ Created on :** {date_creation_date} ({relative_creation_date})\n**💥 Owner :** {owner} (id : `{owner_id}`)\n**💎 Boost tier :** `{premium_tier}` (with `{premium_sub_tier} boosts`)\n**🔐 Verification level :** `{verification_level}`"
                    },
                    {
                        "name": "__Statistics__",
                        "value": "**:busts_in_silhouette: Member count :** `{member_count} members`\n**- 🧔 Hoomans :** `{humain_count} ({humain_count_percent}%)`\n**- 🤖 Bots :** `{bot_count} ({bot_count_percent}%)`\n**📚 Total channels :** `{channel_count}`\n**- 🗃 Categories :** `{category_count}`\n**- 💬 Text :** `{text_count} ({text_count_percent}%)`\n**- 🔊 Voice :** `{voice_count} ({voice_count_percent}%)`"
                    },
                    {
                        "name": "__Roles__"
                    },
                    {
                        "name": "__Emojis__",
                        "value": "(。_。) No emoji found."
                    }
                ]
            }
        }
        self.get_user_info = {
            "loading_embed": {
                "description": "Searching..."
            },
            "embed": {
                "title": "User info",
                "fields": [
                    {
                        "name": "__Main information__",
                        "value": "**#️⃣ Username and tag :** `{user}`\n**🆔 ID :** `{user_id}`\n**⏲ Account created on :** {date_creation_date} ({relative_creation_date})\n**🤖 Is a bot :** `{is_bot}`\n**:busts_in_silhouette: Servers in common :** `{common_serv}`"
                    },
                    {
                        "name": "__Member related info__",
                        "value": "**🎭 Nickname :** `{nickname}`\n**🚪Joined the server on :** {joined_at} ({relative_joined_at})\n**🎨 Activity :** `{activity}`\n**Status :** `{status}`\n**Top role :** {top_role}"
                    }
                ]
            }
        }
