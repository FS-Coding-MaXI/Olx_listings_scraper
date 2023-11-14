import discord
from discord.ext import commands
from discord.ext import tasks
from olx_scraper import OlxScraper
from listings import Listings
from settings import LOG_PATH
import os
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


class MyBot(commands.Bot):
    def __init__(self, command_prefix: str, self_bot: bool):
        super().__init__(
            command_prefix=command_prefix,
            intents=discord.Intents.all(),
            self_bot=self_bot,
        )
        self.add_commands()
        self.LOG_CHANNEL = 1173703610362765332
        self.LISTING_CHANNEL = 1173703610362765332
        self.scraper = OlxScraper()
        self.listings = Listings()
        self.logger = logging.getLogger(__name__)

    async def on_ready(self) -> None:
        self.scraper.start_requests_session()
        self.first_run = True
        self.scrap.start()

    def add_commands(self):
        @self.command(name="status", pass_context=True)
        async def status(ctx) -> None:
            await ctx.channel.send("Kurwa dzialam " + ctx.author.name)

        @self.command(name="ping")
        async def ping(ctx) -> None:
            await ctx.send("pong")

        @self.command(name="start")
        async def start(ctx) -> None:
            self.scrap.start()

        @self.command(name="stop")
        async def stop(ctx) -> None:
            self.scrap.cancel()

        @self.command(name="clean", pass_context=True)
        async def clean(ctx, amount):
            await ctx.channel.purge(limit=int(amount))

        @self.command(name="first", pass_context=True)
        async def first(ctx):
            await self.send_csv()

    # Takes listing and sends to specific channel
    async def send_new_listing(self, listing) -> None:
        channel = self.get_channel(
            self.LISTING_CHANNEL
        )  # Specify channel to which we want to send message

        embed = discord.Embed(
            title=f"{listing.listing_name}", url=f"{listing.link}", color=0x50D68D
        )
        embed.set_thumbnail(url=self.scraper.get_single_listing_photo(listing.link))
        embed.add_field(name="CENA: ", value=f"**{listing.price}**", inline="false")
        embed.set_footer(
            text="by OLX Scraper", icon_url="https://i.imgur.com/hUhyNEL.jpeg"
        )
        await channel.send(embed=embed)  # Send formatted message

    async def send_csv(self) -> None:
        self.listings.listings_to_csv()
        channel = self.get_channel(
            self.LISTING_CHANNEL
        )  # Specify channel to which we want to send message
        embed = discord.Embed(title=f"First scrap result", color=0x50D68D)
        file = discord.File(LOG_PATH)
        if not os.path.isdir("logs"):
            os.mkdir("logs")
        await channel.send(embed=embed)
        await channel.send(file=file)

    async def send_error(self, e) -> None:
        channel = self.get_channel(self.LOG_CHANNEL)
        await channel.send(f"Error occured:\n {e}")

    # Background loop which every minute checks if there is new listng if so, post it
    @tasks.loop(minutes=0.5)
    async def scrap(self) -> None:
        try:
            self.scraper.get_all_pages()
            for p in range(self.scraper.page_number):
                self.listings.add_unv_listings(self.scraper.get_listings_from_page(p))
                self.listings.validate_listings(self.first_run)

            if self.first_run:
                self.listings.sort_listings_by_price()
                self.listings.sort_listings_by_key_priority()
                self.first_run = False

            if self.listings.if_new_listing() and not self.first_run:
                await self.send_new_listing(self.listings.find_new_listing())
                self.listings.listings_to_csv()
        except Exception as e:
            await self.error(e)

    async def error(self, exception):
        """Log Errors caused by Updates."""
        self.logger.error(f"Caused error {exception}", exc_info=True)
