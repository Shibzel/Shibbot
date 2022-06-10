"""Surely a wrong way to do this but watever."""


class English:
    def __init__(self):
        self.DEFAULT_REQUESTED_FOOTER = "Requested by {author}."

        # ping.py cog
        self.ping = {
            "embed": {
                "title": "🏓 Pong !",
                "description": "Shibbot's latency : `{ping}ms`\nMachine load : `CPU: {cpu}%` `RAM: {ram}%`"
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
                "description": "You can't do that. You're missing {permissions} permission(s) to run this command."
            },
            "BotMissingPermissions": {
                "description": "It seems that the bot is missing permissions, if you can manage roles putting Shibbot's role higher may be a solution."
            },
            "BadArgument": {
                "description": "Sorry, bad argument(s). Use the `help` command to get the list of commands."
            },
            "CommandError": {
                "description": " Something went wrong, I couldn't do that.",
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
                    "description": "I couldn't find anything for '{article}', try again."
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
        self.plugins = {
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
            }
        }
        self.change_prefix = {
            "checks": {
                "missing_args": {
                    "description": "Gimme a prefix to change (must be lower than 8 caracters) !\nUsage : `prefix [prefix]`"

                },
                "length_exceeded": {
                    "title": "Oops...",
                    "description": "The prefix must have less than 8 caracters !"

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
            }
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


class French(English):
    def __init__(self):
        super().__init__()

        self.ping = {
            "embed": {
                "title": "🏓 Pong !",
                "description": "Latence de Shibbot : `{ping}ms`\nUtilisation machine : `CPU: {cpu}%` `RAM: {ram}%`"
            }
        }
