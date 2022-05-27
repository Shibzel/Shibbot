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
        self.CommandOnCooldown = {
            "description": "Wait, wait ! This command is on cooldown, you cannot use it until this message disappears (`{secs} second(s)`)."
        }
        self.PrivateMessageOnly = {
            "description": "This command is dm only."
        }
        self.NoPrivateMessage = {
            "description": "This command is guild only."
        }
        self.NotOwner = {
            "description": "You're not my owner, you can't use this command."
        }
        self.UserNotFound = {
            "description": "Couldn't find that user."
        }
        self.ChannelNotFound = {
            "description": "Couldn't find that channel."
        }
        self.NSFWChannelRequired = {
            "description": "This channel {channel} isn't for NSFW content ! Kids might be shocked."
        }
        self.MissingPermissions = {
            "description": "You can't do that. You're missing {permissions} permission(s) to run this command."
        }
        self.BotMissingPermissions = {
            "description": "It seems that the bot is missing permissions, if you can manage roles putting Shibbot's role higher may be a solution."
        }
        self.BadArgument = {
            "description": "Sorry, bad argument(s). Use the `help` command to get the list of commands."
        }
        self.CommandError = {
            "description": " Something went wrong, I couldn't do that.",
            "footer": "If the problem persists, contact the owner of the bot : {owner}.",
            "dissmiss": "dissmiss"
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
                "description": "{user} (id : `{user_id}`) has been banned by {mod}\nReason : {reason}."
            }
        }
        self.log_on_member_unban = {
            "embed": {
                "action": "Kick",
                "description": "{user} (id : `{user_id}`) is now unbanned."
            }
        }
        self.log_unmute = {
            "embed": {
                "action": "Unmute",
                "description": "`{member}` (id : `{member_id}`) has been unmuted"
            }
        }
        self.clear = {
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


class French(English):
    def __init__(self):
        super().__init__()

        self.ping = {
            "embed": {
                "title": "🏓 Pong !",
                "description": "Latence de Shibbot : `{ping}ms`\nUtilisation machine : `CPU: {cpu}%` `RAM: {ram}%`"
            }
        }
