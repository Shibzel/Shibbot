import discord
from discord.ext import commands
from typing import List


class ImageViewer(discord.ui.View):
    DEFAULT_NEXT_BUTTON = discord.ui.Button(
        label="Next",
        style=discord.ButtonStyle.green
    )
    DEFAULT_PREVIOUS_BUTTON = discord.ui.Button(
        label="Previous",
        style=discord.ButtonStyle.gray
    )

    def __init__(
        self,
        ctx: commands.Context,
        image_urls: List[str],
        embed: discord.Embed = discord.Embed(color=discord.Color.dark_gold()),
        next_button: discord.ui.Button = DEFAULT_NEXT_BUTTON,
        previous_button: discord.ui.Button = DEFAULT_PREVIOUS_BUTTON,
        *args, **kwargs
    ):
        self.context = ctx
        self.page = 0
        self.embed = embed
        self.urls = image_urls
        self.next_button = next_button
        self.previous_button = previous_button

        self.next_button.callback = self.next_button_callback
        self.previous_button.callback = self.previous_button_callback

        super().__init__(self.previous_button, self.next_button, *args, **kwargs)

    async def next_button_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.context.author.id:
            return

    async def previous_button_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.context.author.id:
            return
