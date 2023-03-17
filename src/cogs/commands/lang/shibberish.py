from .en import English

class Shibberish(English):
    PING_EMBED_TITLE = "boing"
    PING_EMBED_DESCRIPTION = "shibebot sped : `{ping}ms`\ncheeseburgers : `CPU: {cpu}%` `RAM: {ram}%`"

    SHOW_HELP_OPTION_HOME_LABEL = "hoom"
    SHOW_HELP_TITLE = "__**shibebot help!**__"
    SHOW_HELP_DESCRIPTION = "**hemlo 👋 ! i'm shibebot**, such multipurpose Discord botto, many skillz, can help much with modz, search much on wikipedias, send many memes, and much other wow things!"
    SHOW_HELP_FIELD1_NAME = "blabla" # TODO: Complete this field
    SHOW_HELP_FIELD1_VALUE = "blabla"
    SHOW_HELP_FIELD2_NAME = "new stuff in dis version?"
    SHOW_HELP_FIELD2_VALUE = "wow! much new things added to shibebot! check them out on [our github's releases]({github_link}])!"
    SHOW_HELP_FIELD3_NAME = "need help :"
    SHOW_HELP_FIELD3_VALUE = "prefixes are `{prefix}` and `/`!!! to see what I can do, click on da bar bellow and choose one of da options to much excite ⬇️"
    SHOW_HELP_FOOTER = "things: [] need, <> not need"
    #SHOW_HELP_FOOTER_HOME = ()
    SHOW_HELP_COMMANDS_FIELD_NAME = "commandz :"
    
    CHANGE_PREFIX_TITLE = "dun !"
    CHANGE_PREFIX_DESCRIPTION = "vewy success ! prefixe has been changed to `{prefix}`."

    CHANGE_LANG_MENU_TITLE = "shibe langage"
    CHANGE_LANG_MENU_DESCRIPTION = "what shibebot will speak now ?"
    CHANGE_LANG_DONE_TITLE = "dun !"
    CHANGE_LANG_DONE_DESCRIPTION = "shibebot will now speak in his nativ langage : **{language_flag} {language}**! such polyglot!"

    ENABLE_PLUGINS_PLACEHOLDER = "click on me!!!!"
    ENABLE_PLUGIN_MENU_TITLE = "pluginz"
    ENABLE_PLUGIN_MENU_DESCRIPTION = "pluginz ar shibebot featurz, click to enable!!"
    ENABLE_PLUGIN_DONE_TITLE = "dun !"
    ENABLE_PLUGIN_DONE_DESCRIPTION = "updated! wow."

    GET_INVITATIONS_TITLE = "paper plane"
    GET_INVITATIONS_DESCRIPTION = "is user inviting shibebot ??????"
    GET_INVITATIONS_FOOTER = "happy shibe"
    GET_INVITATIONS_INVITE_BOT_BUTTON = "yes!!!!!!!"
    GET_INVITATIONS_INVITE_SERVER_BUTTON = "com 2 shibe server"

    GET_INFOS_TITLE = "aboute shibebot v{version}"
    GET_INFOS_FIELD1_NAME = "its me"
    GET_INFOS_FIELD1_DESCRIPTION = "shibebot is **very cool, open source Discord botto with many features, made to be easy to use and fun!** present on `{n_servers}` servers and watching over `{n_users}` users (for dis instance). created by [{owner}]({owner_github}). awesome!"
    GET_INFOS_FIELD2_NAME = "cheeseburgers"
    GET_INFOS_FIELD2_DESCRIPTION = "bot running on deez cheeseburgers :\n🐍 snake version : `{python_version}`\n⚡ pycord version : `{pycord_version}`\n❤ things on cpu : `{n_threads} things(s) ({cpu_percent}%)`\n📏 RAM : `{ram_usage}/{n_ram}MB`\n🖥 living and sleeping in : `{place}`"
    GET_INFOS_FIELD3_NAME = "Support the project"
    GET_INFOS_FIELD3_DESCRIPTION = "**Much feedbacks, bugz reports, forks on github, and suggestions are all very much welcome!** Wow! Do not hesistate to check out [our issues page](https://github.com/Shibzel/Shibbot/issues) or join [our Discord server](https://discord.gg/TZNWfJmPwj) for dis. You can also tip my owner by doin `tip`."
    GET_INFOS_FIELD4_NAME = "useless stats"
    GET_INFOS_FIELD4_DESCRIPTION = "⏲️ awake since : `{d}d {h}h {m}m {s}s`\n⌨️ times shibebot was bothered : `{commands}`\n⏱️ avewage sped : `{processing_time}ms`\n⭐ vewy biggest server : `{members}` shibes"