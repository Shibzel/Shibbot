from .en import English

class French(English):
    DEFAULT_FOOTER = "Demandé par {author}."

    GET_USER_INFO_TITLE = "Infos Utilisateur"
    GET_USER_INFO_FIELD1_NAME = "__Infos principales__"
    GET_USER_INFO_FIELD1_VALUE = "**#️⃣ Nom d'utilisateur :** `{user}`\n**🆔 ID :** `{user_id}`\n**⏲ Compte créé le :** {date_creation_date} ({relative_creation_date})\n**🤖 Est un bot :** `{is_bot}`\n**:busts_in_silhouette: Serveurs en commun :** `{common_serv}`"
    GET_USER_INFO_FIELD2_NAME = "__Infos liées au serveur__"
    GET_USER_INFO_FIELD2_VALUE = "**🎭 Pseudo :** `{nickname}`\n**A rejoint le server le :** {joined_at} ({relative_joined_at})\n**🎨 Activité :** `{activity}`\n**Statut :** `{status}`\n**Rôle au sommet :** {top_role}"

    GET_SERVER_INFO_TITLE = "Informations sur le serveur"
    GET_SERVER_INFO_DESCRIPTION = "Quelques infos sur **{guild}** :"
    GET_SERVER_INFO_FIELD1_NAME = "__Informations principales__"
    GET_SERVER_INFO_FIELD1_VALUE = """**🔍 Nom :** `{guild_name}`
**🆔 ID :** `{guild_id}`
**⏲ Créé le :** {date_creation_date} ({relative_creation_date})
**💥 Propriétaire :** {owner} (ID : `{owner_id}`)
**💎 Tier de boost :** `{premium_tier}` (avec `{premium_sub_tier} boosts`)
**➿ Bitrate maximum :** `{bitrate}kbps`"""
    GET_SERVER_INFO_FIELD2_NAME = "__Statistiques__"
    GET_SERVER_INFO_FIELD2_VALUE = """**:busts_in_silhouette: Nombre de membres :** `{member_count} members`
**- 🧔 Humains :** `{humain_count} ({humain_count_percent}%)`
**- 🤖 Bots :** `{bot_count} ({bot_count_percent}%)`
**📚 Nombre de salons :** `{channel_count}`
**- 🗃 Cétégories :** `{categories_count}`
**- 💬 Textuels :** `{text_count} ({text_count_percent}%)`
**- 🎫 Forums :** `{forum_count} ({forum_count_percent}%)`
**- 🔊 Vocaux :** `{voice_count} ({voice_count_percent}%)`
**- 📻 Stage :** `{stage_count} ({stage_count_percent}%)`"""
    GET_SERVER_INFO_FIELD3_NAME = "__Roles__"
    GET_SERVER_INFO_FIELD4_NAME = "__Emojis__"
    GET_SERVER_INFO_FIELD4_VALUE = "(。_。) Aucun émoji trouvé."