from discord import ui, ButtonStyle, Embed, Color
from discord.ext import bridge

from src.core import Shibbot
from src.models import PluginCog, EmbedViewer
from src.utils import filter_doubles
from src.utils.json import json_from_urls

from . import English, French


PLUGIN_NAME = "fun"

class Fun(PluginCog):
    def __init__(self, bot):
        self.bot: Shibbot = bot
        super().__init__(
            plugin_name=PLUGIN_NAME,
            name={"en": "Fun", "fr": "Fun"},
            description={"en": "Entertainement", "fr": "Divertissement."},
            languages={"en": English, "fr": French}, emoji="🎉"
        )
        
    async def _image_factory(self, ctx: bridge.BridgeApplicationContext, urls: list[str], next_button_text: str, previous_button_text: str, footer: str):
        next_button = ui.Button(style=ButtonStyle.blurple, label=next_button_text)
        previous_button = ui.Button(style=ButtonStyle.gray, label=previous_button_text)
        
        author = ctx.author
        avatar = author.avatar.url
        embeds = []
        for url in urls:
            embed = Embed(color=Color.dark_gold())
            embed.set_image(url=url)
            embed.set_footer(text=footer.format(user=author), icon_url=avatar)
            embeds.append(embed)
        
        embed_viewer = EmbedViewer(embeds, next_button, previous_button, bot=self.bot, timeout=300)
        await embed_viewer.send_message(ctx)
        
    @bridge.bridge_command(name="shiba", aliases=["shibe", "shibes", "shibas"], description="Shows cute lil' pics of shibes.",
                           description_localizations={"fr": "Affiche de mignonnes petites photos de shibas."})
    async def get_shibe_pictures(self, ctx: bridge.BridgeApplicationContext):
        lang = await self.get_lang(ctx)
        urls = []
        for url_list in filter_doubles(await json_from_urls([f"https://shibe.online/api/shibes?count=100&urls=true&httpsUrls=true"]*2)):
            urls.extend(url_list)
        await self._image_factory(ctx, urls, lang.GET_SHIBES_NEXT_BUTTON, lang.GET_SHIBES_PREVIOUS_BUTTON, lang.DEFAULT_FOOTER)
        
    @bridge.bridge_command(name="cat", aliases=["cats"], description="Shows cute lil' pics of cats.",
                           description_localizations={"fr": "Affiche de mignonnes petites photos de chat."})
    async def get_cat_pictures(self, ctx: bridge.BridgeApplicationContext):
        lang = await self.get_lang(ctx)
        urls = []
        for url_list in filter_doubles(await json_from_urls([f"https://shibe.online/api/cats?count=100&urls=true&httpsUrls=true"]*2)):
            urls.extend(url_list)
        await self._image_factory(ctx, urls, lang.GET_CATS_NEXT_BUTTON, lang.GET_CATS_PREVIOUS_BUTTON, lang.DEFAULT_FOOTER)
    
    @bridge.bridge_command(name="bird", aliases=["birb", "birds"], description="Shows cute lil' pics of birb.",
                           description_localizations={"fr": "Affiche de mignonnes petites photos d'oiseau."})
    async def get_birb_pictures(self, ctx: bridge.BridgeApplicationContext):
        lang = await self.get_lang(ctx)
        urls = []
        for url_list in filter_doubles(await json_from_urls([f"https://shibe.online/api/birds?count=100&urls=true&httpsUrls=true"]*2)):
            urls.extend(url_list)
        await self._image_factory(ctx, urls, lang.GET_BIRDS_NEXT_BUTTON, lang.GET_BIRDS_PREVIOUS_BUTTON, lang.DEFAULT_FOOTER)
        