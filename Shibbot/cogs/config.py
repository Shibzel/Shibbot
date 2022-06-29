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
    @commands.cooldown(1, 180, commands.BucketType.member)
    async def enable_disable_plugin(self, ctx: commands.Context):
        text = self.client.fl(await self.client.get_lang(ctx.guild)).enable_disable_plugins

        async with self.client.aiodb() as db:
            async def plugin_is_enabled(plugin_name):
                async with db.execute(
                    f"SELECT enabled FROM {plugin_name}_plugin WHERE guild_id=?",
                    (ctx.guild.id,)
                ) as cursor:
                    enabled = await cursor.fetchone()
                    if enabled:
                        enabled = enabled[0]
                    return enabled

            embed_text = text["embed"]
            embed = discord.Embed(
                title=embed_text["title"],
                description="| (• ◡•)| "+embed_text["description"],
                color=discord.Color.dark_gold()
            )

            async def callback(interaction: discord.Interaction):
                if interaction.user.id != ctx.author.id:
                    return

                async with self.client.aiodb() as db:
                    for plugin in ["mod", "fun", "tools"]:
                        enabled = 1 if plugin in select.values else 0
                        cursor = await db.execute(
                            f"SELECT * FROM {plugin}_plugin WHERE guild_id=?",
                            (ctx.guild.id,)
                        )
                        if not await cursor.fetchone():
                            await cursor.execute(
                                f"INSERT INTO {plugin}_plugin(guild_id, enabled) VALUES (?,?)",
                                (ctx.guild.id, enabled,)
                            )
                        else:
                            await cursor.execute(
                                f"UPDATE {plugin}_plugin SET enabled=? WHERE guild_id=?",
                                (enabled, ctx.guild.id,)
                            )
                    await db.commit()
                    await cursor.close()
                await interaction.response.send_message(
                    text["content"],
                    ephemeral=True,
                    delete_after=5.0
                )

            options_text = text["options"]
            options = [
                discord.SelectOption(
                    label=options_text["mod"]["label"],
                    emoji="🔨",
                    value="mod",
                    description=options_text["mod"]["description"],
                    default=await plugin_is_enabled("mod")
                ),
                discord.SelectOption(
                    label=options_text["fun"]["label"],
                    emoji="🎊",
                    value="fun",
                    description=options_text["fun"]["description"],
                    default=await plugin_is_enabled("fun")
                ),
                discord.SelectOption(
                    label=options_text["tools"]["label"],
                    emoji="🔍",
                    value="tools",
                    description=options_text["tools"]["description"],
                    default=await plugin_is_enabled("tools")
                ),
            ]
            select = discord.ui.Select(
                placeholder=options_text["placeholder"],
                min_values=0,
                max_values=len(options),
                options=options
            )
            select.callback = callback
            view = discord.ui.View(select)
            await ctx.reply(embed=embed, view=view)

    @commands.command(name="lang", aliases=["setlang"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 180, commands.BucketType.member)
    async def change_language(self, ctx: commands.Context):
        current_lang = await self.client.get_lang(ctx.guild)
        text = self.client.fl(current_lang).change_language

        def is_current_language(lang):
            return lang == current_lang

        embed_text = text["embed"]
        embed = discord.Embed(
            title=embed_text["title"],
            description="| (• ◡•)| "+embed_text["description"],
            color=discord.Color.dark_gold()
        )

        async def callback(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return

            await self.client.fetch_guild(ctx.guild)
            async with self.client.aiodb() as db:
                async with db.execute(
                    "UPDATE guilds SET lang=? WHERE guild_id=?",
                    (select.values[0], ctx.guild.id,)
                ):
                    await db.commit()
            await interaction.response.send_message(
                text["content"],
                ephemeral=True,
                delete_after=5.0
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
        select.callback = callback
        view = discord.ui.View(select)
        await ctx.reply(embed=embed, view=view)

    @commands.command(name="prefix", aliases=["setprefix"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(2, 60, commands.BucketType.member)
    async def change_prefix(self, ctx: commands.Context, prefix: str = None):
        text = self.client.fl(await self.client.get_lang(ctx.guild)).change_prefix
        if not prefix:
            embed_text = text["checks"]["missing_args"]
            return await ctx.reply(
                embed=discord.Embed(
                    description="( ﾉ ﾟｰﾟ)ﾉ "+embed_text["description"],
                    color=discord.Color.dark_gold()
                )
            )
        elif len(prefix) > 8:
            embed_text = text["checks"]["length_exceeded"]
            return await ctx.reply(
                embed=discord.Embed(
                    title=embed_text["title"],
                    description="(；′⌒`) "+embed_text["description"],
                    color=discord.Color.red()
                )
            )

        await self.client.fetch_guild(ctx.guild)
        async with self.client.aiodb() as db:
            async with db.execute(
                "UPDATE guilds SET prefix=? WHERE guild_id=?",
                (prefix, ctx.guild.id,)
            ):
                await db.commit()
        embed_text = text["embed"]
        await ctx.reply(
            embed=discord.Embed(
                title=embed_text["title"],
                description="<a:verified:836312937332867072> " +
                embed_text["description"].format(prefix=prefix),
                color=discord.Color.green()
            )
        )
