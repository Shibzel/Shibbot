from .en import English

class French(English):
    CHANGE_PREFIX_TITLE = "Fait !"
    CHANGE_PREFIX_DESCRIPTION = "Le préfixe a bien été changé pour `{prefix}`."

    CHANGE_LANG_MENU_TITLE = "Langages"
    CHANGE_LANG_MENU_DESCRIPTION = "Choisissez un language à définir au bot pour ce serveur."
    CHANGE_LANG_DONE_TITLE = "Fait !"
    CHANGE_LANG_DONE_DESCRIPTION = "Le langage a bien été défini sur **{language_flag} {language}**."

    ENABLE_PLUGINS_PLACEHOLDER = "Cliquez pour activer un plugin"
    ENABLE_PLUGIN_MENU_TITLE = "Plugins"
    ENABLE_PLUGIN_MENU_DESCRIPTION = "Choisissez les plugins que vous voulez activer pour ce serveur."
    ENABLE_PLUGIN_DONE_TITLE = "Fait !"
    ENABLE_PLUGIN_DONE_DESCRIPTION = "La liste des plugins activés a été mise à jour."