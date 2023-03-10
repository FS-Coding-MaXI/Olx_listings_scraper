import discord
from discord.ext import commands
from discord.ext import tasks
from olx_scraper import OlxScraper
from listings import Listings
from database import Database
import time


class MyBot(commands.Bot):
    def __init__(self, command_prefix: str, self_bot: bool):
        super().__init__(
            command_prefix=command_prefix,
            intents=discord.Intents.all(),
            self_bot=self_bot,
        )
        self.add_commands()
        self.LOG_CHANNEL = 1083820031630114927
        self.LISTING_CHANNEL = 1083725146080149524
        self.scraper = OlxScraper()
        self.listings = Listings()
        self.scraper.start_requests_session()
        self.db = Database("fshramko", "Hermanshs2813")

    async def on_ready(self) -> None:
        channel = self.get_channel(self.LOG_CHANNEL)
        await channel.send("I have started! ")

    def add_commands(self):
        @self.command(name="status", pass_context=True)
        async def status(ctx) -> None:
            print(ctx)
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

    async def log_listing(self, listing) -> None:
        channel = self.get_channel(self.LOG_CHANNEL)
        await channel.send(f"Sending new listing {listing.link}")

    # Takes listing and sends to specific channel
    async def send_listing(self, listing) -> None:
        channel = self.get_channel(
            self.LISTING_CHANNEL
        )  # Specify channel to which we want to send message

        embed = discord.Embed(
            title=f"{listing.listing_name}", url=f"{listing.link}", color=0x50D68D
        )
        # embed.set_thumbnail(url="https://i.imgur.com/6yk5bMu.jpeg")
        embed.add_field(name="CENA: ", value=f"**{listing.price}**", inline="false")
        embed.set_footer(
            text="by OLX Scraper", icon_url="https://i.imgur.com/hUhyNEL.jpeg"
        )

        await channel.send(embed=embed)  # Send formatted message
        time.sleep(5)

    async def send_new_listing(self, ls) -> None:
        # After validating listing which was not posted, call send_listing, and change bool parameter.
        # await self.log_listing(ls)
        await self.send_listing(ls)

    # Background loop which every minute checks if there is new listng if so, post it
    @tasks.loop(minutes=1)
    async def scrap(self) -> None:
        self.scraper.get_all_pages()
        for p in range(self.scraper.page_number):
            self.listings.add_unv_listings(self.scraper.get_listings_from_page(p))
            self.listings.validate_listings()

        for listing in self.listings.val_offers:
            if not self.db.ifExists(listing):
                await self.send_new_listing(listing)
                await self.db.add_listing(listing)
            # else:  # when reach listing which was already posted, stop checking
            #     return None
