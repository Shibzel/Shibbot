class English:
    DEFAULT_FOOTER = "Requested by {author}."

    GET_USER_INFO_TITLE = "User Info"
    GET_USER_INFO_FIELD1_NAME = "__Main Information__"
    GET_USER_INFO_FIELD1_VALUE = "**#️⃣ Username and tag :** `{user}`\n**🆔 ID :** `{user_id}`\n**⏲ Account created on :** {date_creation_date} ({relative_creation_date})\n**🤖 Is a bot :** `{is_bot}`\n**:busts_in_silhouette: Servers in common :** `{common_serv}`"
    GET_USER_INFO_FIELD2_NAME = "__Member Related Info__"
    GET_USER_INFO_FIELD2_VALUE = "**🎭 Nickname :** `{nickname}`\n**🚪Joined the server on :** {joined_at} ({relative_joined_at})\n**🎨 Activity :** `{activity}`\n**Status :** `{status}`\n**Top role :** {top_role}"

    GET_SERVER_INFO_TITLE = "Server Info"
    GET_SERVER_INFO_DESCRIPTION = "Some information about **{guild}** :"
    GET_SERVER_INFO_FIELD1_NAME = "__Main information__"
    GET_SERVER_INFO_FIELD1_VALUE = """**🔍 Name :** `{guild_name}`
**🆔 ID :** `{guild_id}`
**⏲ Created on :** {date_creation_date} ({relative_creation_date})
**💥 Owner :** {owner} (ID : `{owner_id}`)
**💎 Boost tier :** `{premium_tier}` (with `{premium_sub_tier} boosts`)
**➿ Maximum bitrate :** `{bitrate}kbps`"""
    GET_SERVER_INFO_FIELD2_NAME = "__Statistics__"
    GET_SERVER_INFO_FIELD2_VALUE = """**:busts_in_silhouette: Member count :** `{member_count} members`
**- 🧔 Hoomans :** `{humain_count} ({humain_count_percent}%)`
**- 🤖 Bots :** `{bot_count} ({bot_count_percent}%)`
**📚 Total channels :** `{channel_count}`
**- 🗃 Categories :** `{categories_count}`
**- 💬 Text :** `{text_count} ({text_count_percent}%)`
**- 🎫 Forum :** `{forum_count} ({forum_count_percent}%)`
**- 🔊 Voice :** `{voice_count} ({voice_count_percent}%)`
**- 📻 Stage :** `{stage_count} ({stage_count_percent}%)`"""
    GET_SERVER_INFO_FIELD3_NAME = "__Roles__"
    GET_SERVER_INFO_FIELD4_NAME = "__Emojis__"
    GET_SERVER_INFO_FIELD4_VALUE = "(。_。) No emoji found."