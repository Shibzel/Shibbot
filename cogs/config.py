import discord
from discord.ext import commands

from bot import Shibbot


def setup(client):
    client.add_cog(Config(client))


class Config(commands.Cog):
    def __init__(self, client):
        self.client: Shibbot = client

    @commands.command(name="enable", aliases=["disable", "plugin", "plugins"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def enable_disable_plugin(self, ctx: commands.Context):
        text = self.client.fl(self.client.get_lang(ctx)).plugins

        def plugin_is_enabled(plugin_name):
            self.client.cursor.execute(
                f"SELECT enabled FROM {plugin_name}_plugin WHERE guild_id=?",
                (ctx.guild.id,)
            )
            enabled = self.client.cursor.fetchone()
            if enabled:
                enabled = enabled[0]
            return enabled

        embed_text = text["embed"]
        embed = discord.Embed(
            title=embed_text["title"],
            description="| (• ◡•)| "+embed_text["description"],
            color=discord.Color.dark_gold()
        )

        options_text = text["options"]
        options = [
            discord.SelectOption(
                label=options_text["mod"]["label"],
                emoji="🔨",
                value="mod",
                description=options_text["mod"]["description"],
                default=plugin_is_enabled("mod")
            ),
            discord.SelectOption(
                label=options_text["fun"]["label"],
                emoji="🎊",
                value="fun",
                description=options_text["fun"]["description"],
                default=plugin_is_enabled("fun")
            ),
            discord.SelectOption(
                label=options_text["tools"]["label"],
                emoji="🔍",
                value="tools",
                description=options_text["tools"]["description"],
                default=plugin_is_enabled("tools")
            ),
        ]
        select = discord.ui.Select(
            placeholder=options_text["placeholder"],
            min_values=0,
            max_values=len(options),
            options=options
        )

        async def callback(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return

            for plugin in ["mod", "fun", "tools"]:
                enabled = 1 if plugin in select.values else 0
                self.client.cursor.execute(
                    f"SELECT * FROM {plugin}_plugin WHERE guild_id=?",
                    (ctx.guild.id)
                )
                if not self.client.cursor.fetchone():
                    self.client.cursor.execute(
                        f"INSERT INTO {plugin}_plugin(guild_id, enabled) VALUES (?,?)",
                        (ctx.guild.id, enabled,)
                    )
                else:
                    self.client.cursor.execute(
                        f"UPDATE {plugin}_plugin SET enabled=? WHERE guild_id=?",
                        (enabled, ctx.guild.id,)
                    )
            self.client.db.commit()

        select.callback = callback
        view = discord.ui.View(select)
        await ctx.reply(embed=embed, view=view)

    @commands.command(name="lang", aliases=["setlang"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def change_language(self, ctx: commands.Context):
        current_lang = self.client.get_lang(ctx)
        text = self.client.fl(current_lang).change_language

        def is_current_language(lang):
            return lang == current_lang

        embed_text = text["embed"]
        embed = discord.Embed(
            title=embed_text["title"],
            description="| (• ◡•)| "+embed_text["description"],
            color=discord.Color.dark_gold()
        )

        options_text = text["options"]
        select = discord.ui.Select(
            placeholder=options_text["placeholder"],
            options=[
                discord.SelectOption(
                    label=options_text["en"]["label"],
                    description="english : Hello everyone !",
                    value="en",
                    emoji="🇬🇧",
                    default=is_current_language("en")
                ),
                discord.SelectOption(
                    label=options_text["fr"]["label"],
                    description="french : Bonjour à tous !",
                    value="fr",
                    emoji="🇫🇷",
                    default=is_current_language("fr")
                )
            ]
        )

        async def callback(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return

            self.client.fetch_guild(ctx.guild)
            self.client.cursor.execute(
                "UPDATE guilds SET lang=? WHERE guild_id=?",
                (select.values[0], ctx.guild.id,)
            )
            self.client.db.commit()

        select.callback = callback
        view = discord.ui.View(select)
        await ctx.reply(embed=embed, view=view)

    @commands.command(name="prefix", aliases=["setprefix"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(3, 30, commands.BucketType.member)
    async def change_prefix(self, ctx: commands.Context, prefix: str = None):
        text = self.client.fl(self.client.get_lang(ctx)).change_prefix
        if not prefix:
            embed_text = text["checks"]["missing_args"]["embed"]
            return await ctx.reply(
                embed=discord.Embed(
                    description="( ﾉ ﾟｰﾟ)ﾉ "+embed_text["description"],
                    color=discord.Color.dark_gold()
                )
            )
        elif len(prefix) > 8:
            embed_text = text["checks"]["length_exceeded"]["embed"]
            return await ctx.reply(
                embed=discord.Embed(
                    title=embed_text["title"],
                    description="(；′⌒`) "+embed_text["description"],
                    color=discord.Color.red()
                )
            )

        self.client.fetch_guild(ctx.guild)
        self.client.cursor.execute(
            "UPDATE guilds SET prefix=? WHERE guild_id=?",
            (prefix, ctx.guild.id,)
        )
        self.client.db.commit()
        embed_text = text["embed"]
        await ctx.reply(
            embed=discord.Embed(
                title=embed_text["title"],
                description="<a:verified:836312937332867072> " +
                embed_text["description"].format(prefix=prefix),
                color=discord.Color.green()
            )
        )

    @commands.command(name="logs", aliases=["setlogs"])
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(3, 30, commands.BucketType.member)
    async def change_logs_channel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        text = self.client.fl(self.client.get_lang(ctx)).change_logs_channel
        if not channel:
            embed_text = text["checks"]["missing_args"]["embed"]
            return await ctx.reply(
                embed=discord.Embed(
                    description="( ﾉ ﾟｰﾟ)ﾉ "+embed_text["description"],
                    color=discord.Color.dark_gold()
                )
            )

        self.client.cursor.execute(
            "SELECT logs_channel FROM mod_plugin WHERE guild_id=?",
            (ctx.guild.id,)
        )
        logs_channel = self.client.cursor.fetchone()
        if not logs_channel:
            self.client.cursor.execute(
                "INSERT INTO mod_plugin(guild_id, logs_channel) VALUES (?,?)",
                (ctx.guild.id, channel.id)
            )
        else:
            self.client.cursor.execute(
                "UPDATE mod_plugin SET logs_channel=? WHERE guild_id=?",
                (channel.id, ctx.guild.id,)
            )
        self.client.db.commit()
        embed_text = text["embed"]
        await ctx.reply(
            embed=discord.Embed(
                title=embed_text["title"],
                description=f"<a:verified:836312937332867072> " +
                embed_text["description"].format(channel=channel.mention),
                color=discord.Color.green()
            )
        )
