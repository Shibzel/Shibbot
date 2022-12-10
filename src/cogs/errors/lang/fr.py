from .en import English

class French(English):
    ON_COMMAND_ERROR = {
        "BadArgument": "Désolé, mauvais argument(s). Réessayez.",
        "BotMissingPermissions": "On dirait qu'il me manque les permissions nécessaires à la réalisation de cette commande.",
        "ChannelNotFound": "Je n'ai pas pu trouver ce salon.",
        "CommandOnCooldown": "Hé, attends ! Cette commande est en cooldown, attendez que ce message disparaisse pour l'utiliser à nouveau (`{secs} second(s)`).",
        "CommandError": "Une erreur m'a empêché de faire ça.",
        "PrivateMessageOnly": "Cette commande est réservée aux messages privés.",
        "PluginDisabledError": "Le plugin `{plugin}` est désactivé.",
        "UserNotFound": "Je n'ai pas pu trouver cet utilisateur.",
        "MissingArgumentsError": "Utilisation : `{command_usage}`.",
        "MissingPermissions": "Il vous manque la/les permission(s) {permissions} pour utiliser cette commande.",
        "NoPrivateMessage": "Cette commande est réservée aux serveurs.",
        "NotInteractionOwner": "Désolé {user_interacting} mais seulement {interaction_owner} peut interargir avec ça.",
        "NotOwner": "Il semblerait que tu ne soit pas mon propriétaire, l'utilisation de cette commande t'es proscrite.",
        "NSFWChannelRequired": "Le salon {channel} n'autorise pas le contenu nsfw ! Les enfants pourraient être choqués.",
    }
    ON_COMMAND_ERROR_TITLE = "Oops..."
    DISSMISS_BUTTON = "Compris"
