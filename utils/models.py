import discord

class EmbedViewer(discord.ui.View):
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
        next_button:discord.ui.Button=DEFAULT_NEXT_BUTTON,
        previous_button:discord.ui.Button=DEFAULT_PREVIOUS_BUTTON,
        *args, **kwargs
    ):
        self.pages = []
        self.page = 0
        self.next_button = next_button
        self.previous_button = previous_button

    def add_page(self, embed:discord.Embed):
        self.pages.append(embed)

    def clear_pages(self, *args):
        self.pages.clear()