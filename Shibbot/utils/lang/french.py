from .english import English


class French(English):
    def __init__(self):
        super().__init__()

        self.ping = {
            "embed": {
                "title": "🏓 Pong !",
                "description": "Latence de Shibbot : `{ping}ms`\nCharge machine : `CPU: {cpu}%` `RAM: {ram}%`"
            },
            "buttons": {
                "status": "Page de Statut"
            }
        }

        # help.py cog
        self.get_invitation = {
            "embed": {
                "title": "Invitation",
                "description": "Utilisez les boutons ci-dessous pour vous y rendre. Merci si vous invitez Shibbot !",
                "footer": "Image de Shiba appréciant les fonctionnalités de Shibbot. | Shibbot • v{version}",
            },
            "buttons": {
                "bot_invite": "Invite mwa !",
                "support": "Serveur de support"
            }
        }
        self.bot_info = {
            "embed": {
                "title": "A propos de Shibbot",
                "fields": [
                    {
                        "name": "Description",
                        "value": "Shibbot est un bot multifonction présent sur `{n_servers}` serveurs et écrit en Python par JeanLeShiba ([dsc.bio](https://dsc.bio/jls), [github](https://github.com/JeanLeShiba)). Le but est de proposer un bot cool et fun avec de nombreuses fonctionnalités pour les personnes qui gèrent un serveur et les membres eux-mêmes avec des plugins de modération, des utilitaires, du divertissement... Le projet est toujours en bêta donc si vous rencontrez des problèmes contactez le propriétaire en mp ou via le serveur de support."
                    },
                    {
                        "name": "Specs",
                        "value": "Le bot tourne actuellement sur :\n🐍 Version Python : `{python_version}`\n⚡ Version Pycord : `{pycord_version}`\n❤ Coeurs : `{n_threads} thread(s)`\n📏 RAM : `{ram_usage}/{n_ram}MB`\n🖥 Hébergé à : `{place}`"
                    },
                    {
                        "name": "Supportez le projet",
                        "value": "Tout ceci a été réalisé bénévolement sans but de se faire de l'argent, donc pour continuer à faire vivre le projet, considérez faire [un don Paypal]({donation_link}) (merci). Dans le cas où vous voudriez contribuer en trouvant des bugs ou améliorer le code, rendez-vous sur [la page Github](https://github.com/JeanLeShiba/Shibbot) ou contactez moi par l'un des moyens cités ci-dessus."
                    }
                ]
            }
        }
        self.show_help = {
            "embed": {
                "title": "__**Aide Shibbot!**__",
                "description": "**Salut 👋 ! Je suis Shibbot**, un bot capable de faire des choses comme de la modération, des recherches sur Wikipédia, envoyer des memes, etc... Vous souhaitez en apprendre plus sur moi ? Utilisez `botinfo`, wow.",
                "fields": [
                    {
                        "name": "Commandes :",
                        "value": "- `plugins` : Pour activer ou désactiver les plugins du bot (utiliser si le bot est là pour la première fois sur le serveur).\n- `lang` : Change la langue.\n- `prefix` : Pour définir un préfixe personnalisé sur ce serveur."
                    },
                    {
                        "name": "Quoi de neuf ?",
                        "value": "🇫🇷 Support en Français\nPossibilité de kick/ban en une commande\nNormaliser le pseudo d'un membre avec `username`\nChats et Oiseaux ajoutés, Les Capybaras seront peut être ajoutés par la suite."
                    },
                    {
                        "name": "Obtenir de l'aide :",
                        "value": "Le préfixe actuel est `{prefix}`. Pour obtenir la liste des commandes d'une catégorie, cliquez sur la barre si dessous puis sur une des options pour commencer ⬇."
                    }
                ],
                "footer": "Shibbot v{version} | Légende: []: requis • <> : optionel • ⚠ Indisponible / Ne marche pas encore"
            },
            "select": {
                "placeholder": "Sélectionner une catégorie ici :",
                "info": {
                    "label": "Commandes du bot",
                    "description": "Apprenez en plus sur Shibbot et configurez le sur votre serveur"
                },
                "mod": {
                    "label": "Modération",
                    "description": "Vous permet de modérer votre serveur et ses utilisateurs."
                },
                "fun": {
                    "label": "Amusements",
                    "description": "Commandes amusantes. Yay :D"
                },
                "tools": {
                    "label": "Outils",
                    "description": "Outils utiles à utiliser directement dans un salon."
                },
            },
            "buttons": {
                "invite": "Invitez-moi !",
                "support": "Serveur de Support",
                "donate": "Faire un don"
            },
            "info": {
                "description": "**Infos & Configuration :** Apprenez en plus sur Shibbot et configurez le sur votre serveur.",
                "fields": [
                    {
                        "name": "Commands",
                        "value": """
- `help`: Montre cette page
- `invite`: Envoie un lien d'invitation du bot pour l'inviter sur votre serveur ou accéder au serveur de support
- `ping`: Montre le ping de Shibbot
- `plugins` : Pour activer ou désactiver les plugins du bot sur ce serveur (à utiliser si le bot vient de rejoindre pour la première fois)
- `lang` : Change la langue du bot
- `prefix [prefix]` : Pour définir un préfixe personnalisé sur ce serveur
- `avatar <user>` : Montre l'avatar d'un utilisateur
- `uinfo [user]` : Montre des informations sur l'utilisateur spécifié
- `serverinfo` : Montre des informations sur ce serveur
"""
                    }
                ]
            },
            "mod": {
                "description": "**Modération :** Vous permet de gérer les membres et le serveur avec des commandes simples et des commandes complexes.",
                "fields": [
                    {
                        "name": "Commandes classiques",
                        "value": """
- `logs [channel]` : Définit ou change le salon de journalisation de ce serveur
- `clear [amount] <user>` : Supprime jusqu'à 100 messages à la fois dans le salon
- `warn [member] <reason>` : Avertit un membre
- `clearwarns [user]` : Supprime les avertissements d'un membre
- `mute [member] <reason>` : Rend un memebre muet
- `unmute [member] <reason>` : Rend la parole à un membre
- `kick [member] <reason>` : Expulse un membre
- `ban [user] <reason>` : Bannit un membre
- `unban [user] <reason>` : Retire un utilisateur de la liste des bannis"""
                    },
                    {
                        "name": "Commandes à durée limitée",
                        "value": """
- `tempmute [member] [duration] <reason>` : Rend un membre muet pour la durée spécifiée
- `tempban [member] [duration] <reason>` : Bannit un membre pour la durée spécifiée
"""
                    },
                    {
                        "name": "Commandes spécifiques / Plus complexes",
                        "value": """
- `normalize [member]` : Rétablit le nom par défaut d'un membre
- `nuke` : KADABOOM de jusqu'à 1000 messages dans le salon (dangereux)
- `softban [member] <reason>` : Kick un membre du serveur, supprime tous ses messages des dernières 24h et le réinvite. Utile pour un utilisateur qui s'est fait hacker par exemple
- `multikick [members separated by a space]` : Expulse plusieurs membres en une seule commande
- `multiban [members separated by a space]` : Bannit plusieurs membres en une commande. Équivalent plus violent de multikick"""
                    },
                    {
                        "name": "Commandes d'informations",
                        "value": """
- `warnings [user]` : Liste les avertissements d'un membre
⚠ - `perms [member]` : Liste les permissions d'un membre
⚠ - `roles [member]` : Liste les rôles d'un membre
"""
                    }
                ]
            },
            "fun": {
                "description": "**Amusement :** Commandes amusantes. Yay :D",
                "fields": [
                    {
                        "name": "Commandes",
                        "value": """
- `meme` : Donne un meme aléatoire volé des subreddits les plus drôles
- `nsfwmeme` : Même commande que `meme` mais donne des memes plus adultes / nsfw
- `shiba` : Montre un Shibadorable
- `bird` : Montre un Woiseau
- `cat` : Montre un Chawwww
- `piss` : *piss*
- `twitter` : ratio + L + fatherless + maidenless
- `randnum [a] <b>` : Donne un nombre entre `a` et `b` ou `0` et `a` si `b` n'est pas précisé"""
                    }
                ]
            },
            "tools": {
                "description": "**Outils :** Outils utiles à utiliser directement dans un salon.",
                "fields": [
                    {
                        "name": "Commandes",
                        "value": """
- `wikipedia [search]` : Recherche un article sur Wikipédia
- `translate [language] [sentence]` : Traduit une phrase dans le langage spécifié
- `covid [country]` : Cherche les cas de covid dans un pays spécifié
- `urbandict [word]` : Donne la définition d'un mot dans l'Urban Dictionnary"""
                    }
                ]
            }
        }

        # events.py cog
        self.on_command_error = {
            "CommandOnCooldown": {
                "description": "Hé, attends ! Cette commande est en refroidissement, Il faut attendre que ce message disparaisse pour utiliser à nouveau la commande (`{secs} second(s)`)."
            },
            "PrivateMessageOnly": {
                "description": "Cette commande est réservée aux messages privés."
            },
            "NoPrivateMessage": {
                "description": "Cette commande est réservée aux serveurs."
            },
            "NotOwner": {
                "description": "Tu n'es pas mon créateur, tu ne peux utilser cette commande."
            },
            "UserNotFound": {
                "description": "Je n'ai pas pu trouver cet utilisateur."
            },
            "ChannelNotFound": {
                "description": "Je n'ai pas pu trouver ce salon."
            },
            "NSFWChannelRequired": {
                "description": "Le salon {channel} n'autorise pas le contenu nsfw ! Les âmes sensibles pourraient être choquées."
            },
            "MissingPermissions": {
                "description": "Il vous manque la/les permission(s) {permissions} pour utiliser cette commande.",
                "and": "et"
            },
            "BotMissingPermissions": {
                "description": "On dirait qu'il me manque les permissions nécessaires à la réalisation de cette commande. Il faudrait déplacer mon rôle plus haut dans la liste de rôles, ou la commande n'est pas réalisable"
            },
            "BadArgument": {
                "description": "Désolé, mauvais argument, la commande `help` pourrait vous aider."
            },
            "CommandError": {
                "description": "Une erreur m'a empêché de faire ça.",
                "footer": "Si le problème persiste, contactez le créateur de Shibbot : {owner}.",
                "dissmiss": "Annuler"
            }
        }

        # tools.py cog
        self.urbain_dictionary = {
            "checks": {
                "missing_args": {
                    "description": "Me donner un mot à chercher sur l'Urban Dictionnary !\nUsage : `udict [mot]`"
                }
            },
            "embed": {
                "fields": [
                    {
                        "name": "Définition de {word} par '{author}'"
                    },
                    {
                        "name": "Exemple"
                    }
                ]
            },
            "buttons": {
                "next": "Prochaine Définition",
                "previous": "Définition Précédente"
            }
        }
        self.get_covid_stats = {
            "checks": {
                "missing_args": {
                    "description": "Donnez moi un pays ou utilisez `world` pour obtenir les données mondiales !\nUsage : `covid [pays]`"
                }
            },
            "loading_embed": {
                "title": "Veuillez patienter...",
                "description": "Je récupère les données..."
            },
            "embed": {
                "title": "Statut COVID-19 pour le pays {country}",
                "description": "Voilà les Statistiques :",
                "fields": [
                    {
                        "name": "Cas"
                    },
                    {
                        "name": "Nombre total de cas"
                    },
                    {
                        "name": "Morts"
                    },
                    {
                        "name": "Nombre total de morts"
                    },
                    {
                        "name": "Soignés"
                    },
                    {
                        "name": "Actifs"
                    },
                    {
                        "name": "Cas critiques"
                    },
                    {
                        "name": "Cas pour 1 Million"
                    },
                    {
                        "name": "Morts pour 1 Million"
                    },
                    {
                        "name": "Tests totaux"
                    },
                    {
                        "name": "Tests pour 1 Million"
                    },
                    {
                        "name": "Prenez garde :",
                        "value": "L'information donnée ici peut ne pas être à jour et précise. Source : [www.worldometers.info](http://www.worldometers.info)."
                    }
                ]
            }
        }
        self.translate_text = {
            "checks": {
                "missing_args": {
                    "description": "Donnez moi un langage et du texte à traduire !\nUsage : `trans [language] [sentence]`"
                },
                "bad_args": {
                    "title": "Essayez encore !",
                    "description": "Pas de support pour le langage spécifié."
                },
                "unavalaible": {
                    "title": "Indisponibloe...",
                    "description": "Service indisponible, réessayez plus tard."
                }
            },
            "embed": {
                "title": "Traduction",
                "fields": [
                    {
                        "name": "Texte originel :"
                    },
                    {
                        "name": "Texte traduit :"
                    }
                ]
            }
        }
        self.search_on_wikipedia = {
            "checks": {
                "missing_args": {
                    "description": "Donnez moi quelque chose à chercher !\nUsage : `wiki [article]`"
                },
                "not_found": {
                    "description": "Je n'ai rien put trouver pour '{article}', Réessayez."
                }
            },
            "selection_embed": {
                "description": "Utilisez la barre ci dessous pour obtenir l'objet de votre choix ! (Il ne mordra pas)"
            },
            "select": {
                "placeholder": "Sélectionnez un article ici :"
            },
            "loading_embed": {
                "title": "Veuillez patienter...",
                "description": "Je récupère les données... ça peut prendre une petite seconde."
            }
        }

        # fun.py cog
        self.get_random_number = {
            "checks": {
                "missing_args": {
                    "description": "Donnez moi un nombre ou deux !\nUsage : `randint [x] <y>`"

                }
            }
        }
        self.shibes_viewer = {
            "buttons": {
                "previous": "Shiba précédent",
                "next": "Shiba suivant"
            }
        }
        self.cats_viewer = {
            "buttons": {
                "previous": "Chat précédent",
                "next": "Chat suivant"
            }
        }
        self.birds_viewer = {
            "buttons": {
                "previous": "Oiseau précédent",
                "next": "Oiseau suivant"
            }
        }
        self.meme_viewer = {
            "buttons": {
                "previous": "Meme précédent",
                "next": "Meme suivant"
            }
        }
        self.nsfw_meme_viewer = {
            "buttons": {
                "previous": "Meme précédent",
                "next": "Meme suivant"
            }
        }

        # config.py cog
        self.enable_disable_plugins = {
            "embed": {
                "title": "Plugins",
                "description": "Utilisez la barre ci dessous pour choisir les plugins que vous souhaitez activer ou désactiver."
            },
            "options": {
                "mod": {
                    "label": "Modération",
                    "description": "Vous permet de gérer les membres et le serveur."
                },
                "fun": {
                    "label": "Amusement",
                    "description": "Commandes amusantes. Yay :D"
                },
                "tools": {
                    "label": "Outils",
                    "description": "Outils utiles à utiliser directement dans un salon."
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
