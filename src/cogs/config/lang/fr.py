from .en import English

class French(English):
    PING_EMBED_TITLE = "Pong"
    PING_EMBED_DESCRIPTION = "Latence de Shibbot : `{ping}ms`\nUtilisation machine : `CPU: {cpu}%` `RAM: {ram}%`"

    GET_INVITATIONS_TITLE = "Invitations"
    GET_INVITATIONS_DESCRIPTION = "Utilisez l'un des bouttons ci-dessous pour accéder à ce que vous souhaitez (merci si vous invitez Shibbot !)."
    GET_INVITATIONS_FOOTER = "Image d'un shiba appréciant les fonctionnalités de Shibbot."
    GET_INVITATIONS_INVITE_BOT_BUTTON = "Invite mwa !"
    GET_INVITATIONS_INVITE_SERVER_BUTTON = "Serveur de Shibbot"