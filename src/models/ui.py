import discord
from discord import ui
from discord.ext import bridge

from ..logging import Logger


logger = Logger(__name__)

class CustomView(ui.View):
    def __init__(self, *items: ui.Item, bot = None, disable_on_timeout: bool = True, **kwargs):
        self.bot = bot
        super().__init__(*items, disable_on_timeout=disable_on_timeout, **kwargs)

    async def on_error(self, error: Exception, item: ui.Item, interaction: discord.Interaction) -> None:
        logger.error(f"An unexpected error occured with item {item}.", error)

    async def on_timeout(self):
        if self.disable_on_timeout:
            try:
                if self._message:
                    for child in self.children:
                        if isinstance(child, ui.Button) and child.url:
                            continue
                        child.disabled = True
                    await self._message.edit(view=self) 
            except discord.NotFound:
                pass

class EmbedViewer(CustomView):
    def __init__(self, embeds: list[discord.Embed], next_button: discord.ui.Button, previous_button: discord.ui.Button,
                 use_extremes: bool = False, bot = None, *args, **kwargs):
        super().__init__(*args, bot=bot, **kwargs)
        self.embeds = tuple(embeds)
        self.page = 0
        
        self.skip_button = discord.ui.Button(emoji="⏩")
        self.skip_button.callback = self.skip_button_callback
            
        self.next_button = next_button
        self.next_button.callback = self.next_button_callback
        if len(embeds) <= 1:
            self.next_button.disabled = True
            self.skip_button.disabled = True
            
        self.previous_button = previous_button
        self.previous_button.callback = self.previous_button_callback
        self.previous_button.disabled = True
        
        self.back_button = discord.ui.Button(emoji="⏪")
        self.back_button.callback = self.back_button_callback
        self.back_button.disabled = True
        
        if use_extremes:
            self.add_item(self.back_button)
        self.add_item(self.previous_button)
        self.add_item(self.next_button)
        if use_extremes:
            self.add_item(self.skip_button)
         
    async def send_message(self, ctx: bridge.BridgeApplicationContext, *args, **kwargs):
        await ctx.respond(embed=self.embeds[self.page], view=self, *args, **kwargs)
        
    async def edit_message(self, interaction, embed, *args, **kwargs):
        await interaction.response.edit_message(embed=embed, view=self, *args, **kwargs)
        
    async def step(self, interaction):
        embed = self.embeds[self.page]
        if embed == self.embeds[-1]:
            self.next_button.disabled = True
            self.skip_button.disabled = True
        self.previous_button.disabled = False
        self.back_button.disabled = False
        await self.edit_message(interaction, embed)
        
    async def back(self, interaction):
        embed = self.embeds[self.page]
        if embed == self.embeds[0]:
            self.previous_button.disabled = True
            self.back_button.disabled = True
        self.next_button.disabled = False
        self.skip_button.disabled = False
        await self.edit_message(interaction, embed)
        
    async def next_button_callback(self, interaction: discord.Interaction):
        self.page += 1
        await self.step(interaction)        

    async def skip_button_callback(self, interaction: discord.Interaction):
        self.page = len(self.embeds)-1
        await self.step(interaction)  
              
    async def previous_button_callback(self, interaction: discord.Interaction):
        self.page -= 1
        await self.back(interaction)

    async def back_button_callback(self, interaction: discord.Interaction):
        self.page = 0
        await self.back(interaction)  