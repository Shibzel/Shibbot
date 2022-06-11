import asyncio
from typing import Callable, List, Any, Union

import discord
from discord.ext import commands


class EmbedViewer(discord.ui.View):
    def __init__(
        self,
        ctx: commands.Context,
        list_of_items: List[Any],
        embed_generator: Union[discord.Embed, Callable],
        next_button: discord.ui.Button,
        previous_button: discord.ui.Button,
        *args, **kwargs
    ):
        self.context = ctx
        self.list_of_items = list_of_items
        self.embed_generator = embed_generator

        self.page = 0

        self.next_button = next_button
        self.previous_button = previous_button
        if len(list_of_items) <= 1:
            self.next_button.disabled = True
        self.next_button.callback = self.next_button_callback
        self.previous_button.disabled = True
        self.previous_button.callback = self.previous_button_callback

        super().__init__(
            self.previous_button,
            self.next_button,
            *args, **kwargs
        )

    def get_first_page(self):
        return self.embed_generator(self.list_of_items[0])

    async def next_button_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.context.author.id:
            return

        self.page += 1
        item = self.list_of_items[self.page]
        if item == self.list_of_items[-1]:
            self.next_button.disabled = True
        self.previous_button.disabled = False
        await interaction.response.edit_message(
            embed=self.embed_generator(item),
            view=self
        )

    async def previous_button_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.context.author.id:
            return

        self.page -= 1
        item = self.list_of_items[self.page]
        if item == self.list_of_items[0]:
            self.previous_button.disabled = True
        self.next_button.disabled = False
        await interaction.response.edit_message(
            embed=self.embed_generator(item),
            view=self
        )
