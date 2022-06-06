"""Surely a wrong way to do this but watever."""


class English:
    def __init__(self):
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
                    "embed": {
                        "description": "Gimme a prefix to change (must be lower than 8 caracters) !\nUsage : `prefix [prefix]`"
                    }
                },
                "length_exceeded": {
                    "embed": {
                        "title": "Oops...",
                        "description": "The prefix must have less than 8 caracters !"
                    }
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
                    "embed": {
                        "description": "Gimme a logs channel to define ! Usage : `logs [channel]`"
                    }
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
                    "embed": {
                        "description": "Gimme a number of messages to clear and optionally an user !\nUsage : `clear [amount] <user>`"
                    }
                }
            },
            "member_clear": {
                "embed": {
                    "title": "Done !",
                    "description": "Deleted `{n_messages}` messages of {member}.",
                    "footer": "The messages older than 2 weeks cannot be deleted by the bot (Discord restrictions)."
                }
            },
            "channel_clear": {
                "embed": {
                    "title": "Done !",
                    "description": "Removed `{n_messages}` messages in this channel."
                }
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
                    "embed": {
                        "description": "Gimme a member to warn !\nUsage : `warn [member] <reason>`"
                    }
                }
            },
            "embed": {
                "title": "Warned !",
                "description": "<a:verified:836312937332867072> You've warned {member}. They now have `{n_warns}` warn(s) !\nReason : {reason}"
            },
            "log": {
                "embed": {
                    "action": "Warn n°{n_warns}",
                    "description": "{member} (id : `{member_id}`) has been warned by {mod}.\nReason : {reason}."
                }
            },
            "pm": {
                "embed": {
                    "description": "You've been warned on **{guild}**.\nReason : {reason}."
                }
            }
        }
        self.clear_user_warns = {
            "checks": {
                "missing_args": {
                    "embed": {
                        "description": "Gimme a user with warns to clean !\nUsage : `clearwarns [member] <reason>`"
                    }
                }
            },
            "embed": {
                "title": "Infractions cleared !",
                "description": "All the infractions of {member} has been removed."
            },
            "log": {
                "embed": {
                    "action": "Warns clear",
                    "description": "{mod} cleared all the warns of {member}.\nReason : {reason}."
                }
            }
        }
        self.show_warnings = {
            "checks": {
                "missing_args": {
                    "embed": {
                        "description": "Gimme a user to search !\nUsage : `warnings [member] <reason>`"
                    }
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
                    "embed": {
                        "description": "Gimme a member to mute !\nUsage: `mute[member] <reason>`"
                    }
                },
                "already_muted": {
                    "embed": {
                        "title": "Oops...",
                        "description": "This member is already muted !"
                    }
                }
            },
            "embed": {
                "title": "Muted !",
                "description": "Just muted {member}.\nReason : {reason}"
            },
            "log": {
                "embed": {
                    "action": "Mute",
                    "description": "{member} (id : `{member_id}`) has been muted by {mod}.\nReason : {reason}."
                }
            },
            "pm": {
                "embed": {
                    "description": "You've been muted on **{guild}**.\nReason : {reason}."
                }
            }
        }
        self.tempmute_member = {
            "checks": {
                "missing_args": {
                    "embed": {
                        "description": "Gimme a member to tempmute !\nUsage: `tmute [member] [duration] <reason>`"
                    }
                },
                "already_muted": {
                    "embed": {
                        "title": "Oops...",
                        "description": "This member is already muted !"
                    }
                }
            },
            "embed": {
                "title": "Muted !",
                "description": "{member} is now tempmuted for `{duration}`.\nReason : {reason}"
            },
            "log": {
                "embed": {
                    "action": "Tempmute",
                    "description": "{member} (id : `{member_id}`) has been tempmuted by {mod} for `{duration}`.\nReason : {reason}."
                }
            },
            "pm": {
                "embed": {
                    "description": "You've been tempmuted on **{guild}** for `{duration}`.\nReason : {reason}."
                }
            }
        }
        self.unmute_member = {
            "checks": {
                "missing_args": {
                    "embed": {
                        "description": "Gimme a member to unmute !\nUsage: `tmute [member]`"
                    }
                },
                "not_muted": {
                    "embed": {
                        "title": "Oops...",
                        "description": "This member is not muted !"
                    }
                }
            },
            "embed": {
                "title": "Muted !",
                "description": "{member} is now unmuted."
            },
            "pm": {
                "embed": {
                    "description": "You've been unmuted from **{guild}**."
                }
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
