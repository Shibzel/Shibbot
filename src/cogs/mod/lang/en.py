class English:
    NO_REASON_PLACEHOLDER = "No reason provided."
    
    ON_KICK_TITLE = "Kick"
    ON_KICK_DESCRIPTION = "{member.mention} ({member}) has been kicked by {mod.mention}.\nReason: {reason}"
    
    ON_BAN_TITLE = "Ban"
    ON_BAN_DESCRIPTION = "{user.mention} ({user}) has been baned by {mod.mention}.\nReason: {reason}"
    
    ON_UNBAN_TITLE = "Unban"
    ON_UNBAN_DESCRIPTION = "{user.mention} ({user}) has been unbaned by {mod.mention}.\nReason: {reason}"
    
    ON_WARN_TITLE = "Warn n°{warns}"
    ON_WARN_DESCRIPTION = "{member.mention} ({member}) has been warned by {mod.mention}.\nReason: {reason}"
    
    ON_PURGE_TITLE = "Purge"
    ON_PURGE_USER_DESCRIPTION = "`{messages}` of {user.mention} ({user}) has been purged in {channel.mention} by {mod.mention}.\nReason: {reason}"
    ON_PURGE_CHANNEL_DESCRIPTION = "`{messages}` of {channel.mention} has been purged by {mod.mention}.\nReason: {reason}"