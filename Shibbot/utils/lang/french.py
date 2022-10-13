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
                "footer": "Image d'un shiba appréciant les fonctionnalités de Shibbot. | Shibbot • v{version}",
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
                        "value": "Shibbot est un bot multifonction présent sur `{n_servers}` serveurs et écrit en Python par JeanLeShiba ([dsc.bio](https://dsc.bio/jls), [github](https://github.com/JeanLeShiba)). Le but est de proposer un bot sympa et fun avec de nombreuses fonctionnalités pour les personnes qui gèrent un serveur et les membres eux-mêmes avec des plugins de modération, des utilitaires, du divertissement... Le projet est toujours en bêta donc si vous rencontrez des problèmes contactez le propriétaire en mp ou via le serveur de support."
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
                        "value": "🇫🇷 Support en Français\nPossibilité de kick/ban plusieurs personnes en une commande\nNormaliser le pseudo d'un membre avec `username`\nAjout de chats et d'oiseaux."
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
                    "description": "Commandes fun. Yay :D"
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
- `lang` : Change le langage du bot
- `prefix [préfixe]` : Pour définir un préfixe personnalisé sur ce serveur
- `avatar <utilisateur>` : Montre l'avatar d'un utilisateur
- `uinfo [utilisateur]` : Montre des informations sur l'utilisateur spécifié
- `sinfo` : Montre des informations sur ce serveur
"""
                    }
                ]
            },
            "mod": {
                "description": "**Modération :** Aides pour modérer votre serveur.",
                "fields": [
                    {
                        "name": "Commandes classiques",
                        "value": """
- `logs [salon]` : Définit ou change le salon de log de ce serveur
- `clear [quantité] <utilisateur>` : Supprime jusqu'à 100 messages à la fois dans le salon
- `warn [membre] <raison>` : warnst un membre
- `clearwarns [utilisateur]` : Supprime les warns d'un membre
- `mute [membre] <raison>` : Rend un memebre muet
- `unmute [membre] <raison>` : Rend la parole à un membre
- `kick [membre] <raison>` : Expulse un membre
- `ban [utilisateur] <raison>` : Bannit un membre
- `unban [utilisateur] <raison>` : Retire un utilisateur de la liste des bannis"""
                    },
                    {
                        "name": "Commandes à durée limitée",
                        "value": """
- `tempmute [membre] [durée] <raison>` : Rend un membre muet pour la durée spécifiée
- `tempban [membre] [durée] <raison>` : Bannit un membre pour la durée spécifiée
"""
                    },
                    {
                        "name": "Commandes spécifiques / Plus complexes",
                        "value": """
- `normalize [membre]` : Rend "normal" le pseudo d'un membre
- `nuke` : KADABOOM jusqu'à 1000 messages dans le salon (dangereux)
- `softban [membre] <raison>` : Kick un membre du serveur, supprime tous ses messages des dernières 24h et le réinvite. Utile pour un utilisateur qui s'est fait hacker par exemple
- `multikick [membres séparés par un espace]` : Expulse plusieurs membres en une seule commande
- `multiban [membres séparés par un espace]` : Bannit plusieurs membres en une commande. Équivalent plus violent de multikick"""
                    },
                    {
                        "name": "Commandes d'informations",
                        "value": """
- `warnings [utilisateur]` : Liste les warns d'un membre
⚠ - `perms [membre]` : Liste les permissions d'un membre
⚠ - `roles [membre]` : Liste les rôles d'un membre
"""
                    }
                ]
            },
            "fun": {
                "description": "**Amusement :** Commandes fun. Yay :D",
                "fields": [
                    {
                        "name": "Commandes",
                        "value": """
- `meme` : Donne un meme aléatoire volé des subreddits les plus drôles
- `nsfwmeme` : Même commande que `meme` mais donne des memes plus adultes / nsfw
- `shiba` : Montre un Shibadorable
- `bird` : Montre un Woiseau
- `cat` : Montre un Chawwww
- `piss` : *pisse*
- `ratio` : ratio + L + fatherless + maidenless
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
- `covid [pays (en anglais)]` : Cherche les cas de covid dans un pays spécifié
- `urbandict [word]` : Donne la définition d'un mot dans l'Urban Dictionnary"""
                    }
                ]
            }
        }

        # events.py cog
        self.on_command_error = {
            "CommandOnCooldown": {
                "description": "Hé, attends ! Cette commande est en cooldown, Il faut attendre que ce message disparaisse pour utiliser à nouveau la commande (`{secs} second(s)`)."
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
                "description": "On dirait qu'il me manque les permissions nécessaires à la réalisation de cette commande. Il faudrait déplacer mon rôle plus haut dans la liste de rôles ou que je ne peux pas faire ça."
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
                    "description": "Donnez-moi un mot à chercher sur l'Urban Dictionnary !\nUsage : `udict [mot]`"
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
                    "description": "Donnez-moi un pays ou utilisez `world` pour obtenir les données mondiales !\nUsage : `covid [pays]`"
                }
            },
            "loading_embed": {
                "title": "Veuillez patienter...",
                "description": "Je récupère les données..."
            },
            "embed": {
                "title": "Statut COVID-19 pour le pays {country}",
                "description": "Voilà les statistiques :",
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
                    "description": "Donnez-moi un langage et du texte à traduire !\nUsage : `trans [language] [sentence]`"
                },
                "bad_args": {
                    "title": "Essayez encore !",
                    "description": "Pas de support pour le langage spécifié."
                },
                "unavalaible": {
                    "title": "Indisponible...",
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
                    "description": "Donnez-moi quelque chose à chercher !\nUsage : `wiki [article]`"
                },
                "not_found": {
                    "description": "Je n'ai rien put trouver pour '{article}', Réessayez."
                }
            },
            "selection_embed": {
                "description": "Utilisez la barre ci dessous pour obtenir l'objet de votre choix ! (Elle ne mordra pas)"
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
                    "description": "Donnez-moi un nombre ou deux !\nUsage : `randint [x] <y>`"

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
                    "description": "Commandes fun. Yay :D"
                },
                "tools": {
                    "label": "Outils",
                    "description": "Outils utiles à utiliser directement dans un salon."
                },
                "placeholder": "Sélectionnez un plugin ici :"
            },
            "content": "Fait !"
        }
        self.change_prefix = {
            "checks": {
                "missing_args": {
                    "description": "Donnez-moi un préfixe (doit être inférieur à 8 caractères) !\nUsage : `prefix [préfixe]`"

                },
                "length_exceeded": {
                    "title": "Oops...",
                    "description": "Le préfixe ne doit pas dépasser 8 caractères !"

                }
            },
            "embed": {
                "title": "Fait !",
                "description": "Le préfixe a bien été changé pour `{prefix}`."
            }
        }
        self.change_logs_channel = {
            "checks": {
                "missing_args": {
                    "description": "Donnez-moi un salon pour le logging ! Utilisation : `logs [salon]`"

                }
            },
            "embed": {
                "title": "Fait !",
                "description": "Le salon des logs a bien été changé pour {channel}."
            }
        }
        self.change_language = {
            "embed": {
                "title": "Language",
                "description": "Utilisez la barre ci-dessous pour changer de langage."
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
            "content": "Fait !"
        }

        # mod.py cog
        self.log_on_member_remove = {
            "embed": {
                "action": "Kick",
                "description": "{member} (id : `{member_id}`) a été kick par {mod}\nRaison : {reason}."
            }
        }
        self.log_on_member_ban = {
            "embed": {
                "action": "Kick",
                "description": "{member} (id : `{member_id}`) a été banni par {mod}\nRaison : {reason}."
            }
        }
        self.log_on_member_unban = {
            "embed": {
                "action": "Kick",
                "description": "{member} (id : `{member_id}`) n'est plus ban."
            }
        }
        self.log_unmute = {
            "embed": {
                "action": "Unmute",
                "description": "{member} (id : `{member_id}`) n'est plus mute."
            }
        }
        self.log_purge = {
            "embed": {
                "action": "Purge",
                "description": "{mod} a supprimé {n_message} messages dans {channel}."
            },
        }
        self.clear_messages = {
            "checks": {
                "missing_args": {
                    "description": "Donnez-moi un nombre de messages à supprimer et au préalable un utilisateur !\nUsage : `clear [quantité] <utilisateur>`"
                }
            },
            "member_clear": {
                "title": "Fait !",
                "description": "`{n_messages}` messages de {member} ont été supprimés.",
                "footer": "Les messages plus vieux que 2 semaines ne peuvent être supprimés (restriction Discord)."

            },
            "channel_clear": {
                "title": "Fait !",
                "description": "`{n_messages}` messages ont été supprimés dans ce salon."
            }
        }
        self.nuke_channel = {
            "embed": {
                "title": "Ok, ok, attendez une seconde !",
                "description": "Vous êtes sur le point de nuke ce salon et **plus de 1000 messages peuvent-être supprimés**. Etes vous vraiment sûr de vouloir faire ça ?"
            },
            "buttons": {
                "no": "nah c'est bon",
                "yes": "KADABOOOM"
            },
            "done": {
                "title": "Fait !",
                "description": "`{n_messages}` messages ont cessé d'exister, ça a été vraiment efficace !"
            }
        }
        self.warn_member = {
            "checks": {
                "missing_args": {
                    "description": "Donnez-moi un membre à warnsr !\nUsage : `warn [membre] <raison>`"
                }
            },
            "embed": {
                "title": "Warned !",
                "description": "Vous avez warn {member}. Il a désormais `{n_warns}` warn(s) !\nRaison : {reason}"
            },
            "log": {
                "action": "Warn n°{n_warns}",
                "description": "{member} (id : `{member_id}`) a été warn par {mod}.\nRaison : {reason}."
            },
            "pm": {
                "description": "Vous avez été warn sur **{guild}**.\nRaison : {reason}."
            }
        }
        self.clear_user_warns = {
            "checks": {
                "missing_args": {
                    "description": "Donnez-moi un utilisateur avec des warns !\nUsage : `clearwarns [membre] <raison>`"
                }
            },
            "embed": {
                "title": "Infractions effacées !",
                "description": "Toutes les infractions de {member} ont été supprimés."
            },
            "log": {
                "action": "Effacement d'infractions",
                "description": "{mod} a supprimé tous les warns de {member}.\nRaison : {reason}."
            }
        }
        self.show_warnings = {
            "checks": {
                "missing_args": {
                    "description": "Donnez-moi un utilisateur !\nUsage : `warnings [membre] <raison>`"
                }
            },
            "embed": {
                "title": "Infractions",
                "description": "Voici toutes les infractions de {member} (id : `{member_id}`) :",
                "fields": {
                    "no_infra": {
                        "name": "Aucune infraction",
                        "value": "Cet utilisateur n'a pas encore été warn (il doit être un ange... ou les modos font pas leur boulot, jsp)."
                    },
                    "warn": {
                        "name": "Warn n°{n_warn}",
                        "value": "Raison : {reason}\Par {mod} le `{date}`"
                    }
                },
                "buttons": {
                    "previous": "Précédent",
                    "next": "Suivant"
                }
            }
        }
        self.mute_member = {
            "checks": {
                "missing_args": {
                    "description": "Donnez-moi un membre à mute !\nUsage: `mute[membre] <raison>`"

                },
                "already_muted": {
                    "title": "Oops...",
                    "description": "Ce membre est déjà mute !"
                }
            },
            "embed": {
                "title": "Mute !",
                "description": "J'ai mute {member}.\nRaison : {reason}"
            },
            "log": {
                "action": "Mute",
                "description": "{member} (id : `{member_id}`) a été mute par {mod}.\nRaison : {reason}."
            },
            "pm": {
                "description": "Vous avez été mute sur **{guild}**.\nRaison : {reason}."
            }
        }
        self.tempmute_member = {
            "checks": {
                "missing_args": {
                    "description": "Donnez-moi un membre à tempmute !\nUsage: `tmute [membre] [durée] <raison>`"
                },
                "already_muted": {
                    "title": "Oops...",
                    "description": "Ce membre est déjà tempmute !"
                }
            },
            "embed": {
                "title": "Muted !",
                "description": "{member} est désormais tempmute pour `{duration}`.\nRaison : {reason}"
            },
            "log": {
                "action": "Tempmute",
                "description": "{member} (id : `{member_id}`) a été tempmute par {mod} pour `{duration}`.\nRaison : {reason}."
            },
            "pm": {
                "description": "Vous avez été tempmute sur **{guild}** pour `{duration}`.\nRaison : {reason}."
            }
        }
        self.unmute_member = {
            "checks": {
                "missing_args": {
                    "description": "Donnez-moi un membre à unmute !\nUsage: `tmute [membre]`"
                },
                "not_muted": {
                    "title": "Oops...",
                    "description": "Ce membre n'est pas mute !"
                }
            },
            "embed": {
                "title": "Unmute !",
                "description": "{member} n'est désormais plus mute."
            },
            "pm": {
                "description": "Vous avez été unmute sur **{guild}**."
            }
        }
        self.yeet_member = {
            "checks": {
                "missing_args": {
                    "description": "Donnez-moi un membre à expulser !\nUsage : `kick [membre] <raison>`"
                }
            },
            "embed": {
                "title": "Expulsé !",
                "description": "{member} s'est prit un coup de pied au c*l s'est fait dégagé de votre serveur.\nRaison : {reason}"
            },
            "pm": {
                "description": "Vous avez été expulsé de **{guild}**.\nRaison : {reason}"
            }
        }
        self.yeet_members = {
            "checks": {
                "missing_args": {
                    "description": "Donnez-moi des membres à expulser !\nUsage : `mkick [memberes séparés par un espace]`"
                }
            },
            "embed": {
                "title": "Commande d'expulsion de groupe",
                "fields": [
                    {
                        "name": "Expulsion(s) réussie(s)"
                    },
                    {
                        "name": "Expulion(s) raté(s)"
                    }
                ]
            },
            "pm": {
                "description": "Vous avez été expulsé de **{guild}**."
            }
        }
        self.ban_user = {
            "checks": {
                "missing_args": {
                    "description": "Donnez-moi un utilisateur à bannir !\nUsage : `ban [utilisateur] <raison>`"
                }
            },
            "embed": {
                "title": "Banni !",
                "description": "Le marteau du ban s'est abbatu sur {member}.\nRaison : {reason}"
            },
            "pm": {
                "description": "Vous avez été banni de **{guild}**.\nRaison : {reason}"
            }
        }
        self.tempban_member = {
            "checks": {
                "missing_args": {
                    "description": "Donnez-moi un utilisateur à tempban !\nUsage: `tban [utilisateur] [durée] <raison>`"
                }
            },
            "embed": {
                "title": "Banni !",
                "description": "{member} a été banni pour `{duration}`.\nRaison : {reason}"
            },
            "log": {
                "action": "Tempban",
                "description": "{member} (id : `{member_id}`) a été banni par {mod} pour `{duration}`.\nRaison : {reason}."
            },
            "pm": {
                "description": "Vous avez été banni sur **{guild}** pour `{duration}`.\nRaison : {reason}."
            }
        }
        self.softban_member = {
            "checks": {
                "missing_args": {
                    "description": "Donnez-moi un membre à soft-ban !\nUsage : `softban [membre] <raison>`"
                }
            },
            "pm": {
                "description": "Vous avez été soft-ban de **{guild}** pour la raison suivante : '{reason}'.\nUtilisez ce lien pour revenir : {invite}"
            },
            "embed": {
                "title": "Soft-banni !",
                "description": "{member} a été soft-ban.\nRaison : {reason}"
            },
            "log": {
                "action": "Soft-ban",
                "description": "{member} (id : `{member_id}`) a été softban par {mod}.\nRaison : {reason}."
            }
        }
        self.ban_members = {
            "checks": {
                "missing_args": {
                    "description": "Donnez-moi des membres à bannir !\nUsage : `mban [memberes] <raison>`"
                }
            },
            "embed": {
                "title": "Commande de ban de groupe",
                "fields": [
                    {
                        "name": "Ban(s) réussi(s)"
                    },
                    {
                        "name": "Ban(s) raté(s)"
                    }
                ]
            },
            "pm": {
                "description": "Vous avez été banni de **{guild}**."
            }
        }
        self.unban_user = {
            "checks": {
                "missing_args": {
                    "description": "Donnez-moi un membre à débannir !\nUsage: `unban [utilisateur]`"
                }
            },
            "embed": {
                "title": "Débanni !",
                "description": "{member} n'est désormais plus ban."
            },
            "pm": {
                "description": "Vous avez été débanni de **{guild}**."
            }
        }
        self.normalize_nickname = {
            "checks": {
                "missing_args": {
                    "description": "Donnez moi un membre dont je dois normaliser le pseudo !\nUsage : `normalize [membre]`."
                },
                "already_normal": {
                    "title": "Hm.",
                    "description": "`{nickname}` me semble plutôt normal, rien n'a changé."
                }
            },
            "embed": {
                "title": "Aux standarts !",
                "description": "J'ai nettoyé le pseudo de {member}, c'est plus lisible d'un coup."
            }
        }

        # misc.py cog
        self.show_avatar = {
            "embed": {
                "description": "L'avatar de {member} :"
            }
        }
        self.get_guild_info = {
            "loading_embed": {
                "description": "Recherche..."
            },
            "embed": {
                "title": "Infos du serveur",
                "description": "Quelques informations sur **{guild}** :",
                "fields": [
                    {
                        "name": "__Informations principales__",
                        "value": "**🔍 Nom :** `{guild_name}`\n**🆔 ID :** `{guild_id}`\n**⏲ Créé le :** {date_creation_date} ({relative_creation_date})\n**💥 propriétaire :** {owner} (id : `{owner_id}`)\n**💎 Palier de boost :** `{premium_tier}` (avec `{premium_sub_tier} boosts`)\n**🔐 Niveau de vérification :** `{verification_level}`"
                    },
                    {
                        "name": "__Statistiques__",
                        "value": "**:busts_in_silhouette: Total de membres :** `{member_count} membres`\n**- 🧔 Humains :** `{humain_count} ({humain_count_percent}%)`\n**- 🤖 Bots :** `{bot_count} ({bot_count_percent}%)`\n**📚 Total de salons :** `{channel_count}`\n**- 🗃 Catégories :** `{category_count}`\n**- 💬 Texte :** `{text_count} ({text_count_percent}%)`\n**- 🔊 Voix :** `{voice_count} ({voice_count_percent}%)`"
                    },
                    {
                        "name": "__Roles__"
                    },
                    {
                        "name": "__Emojis__",
                        "value": "(。_。) Aucun émoji trouvé."
                    }
                ]
            }
        }
        self.get_user_info = {
            "loading_embed": {
                "description": "Recherche..."
            },
            "embed": {
                "title": "Infos de l'utilisateur",
                "fields": [
                    {
                        "name": "__Informations principales__",
                        "value": "**#️⃣ Nom & tag :** `{user}`\n**🆔 ID :** `{user_id}`\n**⏲ Compte créé le :** {date_creation_date} ({relative_creation_date})\n**🤖 Est un bot :** `{is_bot}`\n**:busts_in_silhouette: Serveurs en commun :** `{common_serv}`"
                    },
                    {
                        "name": "__Infos liés au membre__",
                        "value": "**🎭 Pseudo :** `{nickname}`\n**🚪A rejoint le serveur le :** {joined_at} ({relative_joined_at})\n**🎨 Activité :** `{activity}`\n**Statut :** `{status}`\n**Rôle le plus haut :** {top_role}"
                    }
                ]
            }
        }
