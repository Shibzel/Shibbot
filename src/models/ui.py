import discord


class CustomView(discord.ui.View):
    def __init__(self, *items: discord.ui.Item, bot = None, **kwargs):
        self.bot = bot
        super().__init__(*items, **kwargs)

    async def on_error(self, error, item, interaction):
        if self.bot:
            await self.bot.on_command_error(interaction.message, error)

    async def on_timeout(self):
        if self.disable_on_timeout:
            try:
                if self._message:
                    for child in self.children:
                        if isinstance(child, discord.ui.Button) and child.url:
                            continue
                        child.disabled = True
                    await self._message.edit(view=self) 
            except discord.NotFound:
                pass

class EmbedViewer(CustomView):
    pass