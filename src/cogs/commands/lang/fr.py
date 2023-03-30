from .en import English

class French(English):
    PING_EMBED_TITLE = "🏓 Pong"
    PING_EMBED_DESCRIPTION = "Latence de Shibbot : `{ping}ms`\nUtilisation machine : `CPU: {cpu}%` `RAM: {ram}%`"

    SHOW_HELP_OPTION_HOME_LABEL = "Accueil"
    SHOW_HELP_TITLE = "__**Aide Shibbot!**__"
    SHOW_HELP_DESCRIPTION = "**Salut 👋 ! Je suis Shibbot**, un bot multifonction qui peut par exemple vous aider avec la modération de votre serveur, faire des recherches sur wikipédia, poster des memes et pleins d'autres choses !"
    # SHOW_HELP_FIELD1_NAME = "blabla"
    # SHOW_HELP_FIELD1_VALUE = "blabla"
    SHOW_HELP_FIELD2_NAME = "Quoi de neuf dans cette version ?"
    SHOW_HELP_FIELD2_VALUE = "Pour voir les dernières fonctions ajoutées au bot vous pouvez aller dans [nos releases github]({github_link}) !"
    SHOW_HELP_FIELD3_NAME = "Obtenir de l'aide :"
    SHOW_HELP_FIELD3_VALUE = "Le préfix est `{prefix}`. Pour accéder à la liste de commandes appartenant à l'un de mes cogs, cliquez sur la barre ci-dessous et choisissez l'une des options pour vous y rendre ⬇."
    SHOW_HELP_FOOTER = "Légende: [] requis, <> optionel"
    SHOW_HELP_FOOTER_HOME = ("Conseil: Si l'application ne répond pas, réinvoquez la commande.",)
    SHOW_HELP_COMMANDS_FIELD_NAME = "Commandes :"
    
    CHANGE_PREFIX_TITLE = "Fait !"
    CHANGE_PREFIX_DESCRIPTION = "Le préfixe a bien été changé pour `{prefix}`."

    CHANGE_LANG_MENU_TITLE = "Langages"
    CHANGE_LANG_MENU_DESCRIPTION = "Utilisez la barre ci-dessous pour changer le langage."
    CHANGE_LANG_DONE_TITLE = "Fait !"
    CHANGE_LANG_DONE_DESCRIPTION = "Le langage a bien été défini sur **{language_flag} {language}**. Incroyable."

    ENABLE_PLUGINS_PLACEHOLDER = "Cliquez pour activer un plugin :"
    ENABLE_PLUGIN_MENU_TITLE = "Plugins"
    ENABLE_PLUGIN_MENU_DESCRIPTION = "Un plugin est une fonctionalité activable ou désactivable de Shibbot. Utilisez la barre ci-dessous et cochez ce que vous souhaitez activer."
    ENABLE_PLUGIN_DONE_TITLE = "Fait !"
    ENABLE_PLUGIN_DONE_DESCRIPTION = "La liste des plugins activés a été mise à jour."

    GET_INVITATIONS_TITLE = "Invitations"
    GET_INVITATIONS_DESCRIPTION = "Utilisez l'un des bouttons ci-dessous pour accéder à ce que vous souhaitez (merci si vous invitez Shibbot !)."
    GET_INVITATIONS_FOOTER = "Image d'un shiba appréciant les fonctionnalités de Shibbot."
    GET_INVITATIONS_INVITE_BOT_BUTTON = "Invite mwa !"
    GET_INVITATIONS_INVITE_SERVER_BUTTON = "Serveur de Shibbot"

    GET_INFOS_TITLE = "A propos de Shibbot v{version}"
    GET_INFOS_FIELD1_NAME = "Description"
    GET_INFOS_FIELD1_DESCRIPTION = "Shibbot est **un bot Discord riche en fonctionnalités, open-source designé pour être modulaire et accessible** présent sur `{n_servers}` serveurs et gérant plus de `{n_users}` utilisateurs (pour cette instance), créé par [{owner}]({owner_github})."
    GET_INFOS_FIELD2_NAME = "Specifications"
    GET_INFOS_FIELD2_DESCRIPTION = "Le bot tourne actuellement sur :\n🐍 Version Python : `{python_version}`\n⚡ Version Pycord : `{pycord_version}`\n❤ Coeurs : `{n_threads} thread(s) ({cpu_percent}%)`\n📏 RAM : `{ram_usage}/{n_ram}MB`\n🖥 Hébergé à : `{place}`"
    GET_INFOS_FIELD3_NAME = "Supportez le projet"
    GET_INFOS_FIELD3_DESCRIPTION = "**Tous les retours, rapports de bugs, branches github et suggestions sont le bienvenus !** N'héistez surtout pas à aller voir [la page de rapports de bugs](https://github.com/Shibzel/Shibbot/issues) ou à rejoindre [notre serveur Discord](https://discord.gg/TZNWfJmPwj) pour ça. Vous pouvez aussi faire un don au créateur du bot via la commande `tip`."
    GET_INFOS_FIELD4_NAME = "Stats"
    GET_INFOS_FIELD4_DESCRIPTION = "⏲️ Uptime : `{d}d {h}h {m}m {s}s`\n⌨️ Commandes invoquées : `{commands}`\n⏱️ Temps moyen de réponse : `{processing_time}ms`\n⭐ Plus gros serveur : `{members}` members"