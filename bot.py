import discord
from discord.ext import commands
from discord.ext import tasks
from olx_scraper import OlxScraper
from listings import Listings

scraper = OlxScraper()
listings = Listings()
scraper.start_session()


class MyBot(commands.Bot):
    def __init__(self, command_prefix: str, intents: discord.Intents, self_bot: bool):
        super().__init__(
            command_prefix=command_prefix, intents=intents, self_bot=self_bot
        )
        self.add_commands()
        self.LOG_CHANNEL = 1083820031630114927
        self.LISTING_CHANNEL = 1083725146080149524

    async def on_ready(self) -> None:
        channel = self.get_channel(self.LOG_CHANNEL)
        await channel.send("I have started! ")
        # self.scrap.start()
        await self.scrap()

    def add_commands(self):
        @self.command(name="test_list", pass_context=True)
        async def test_list(ctx) -> None:
            self.send_listing(listings.val_offers[0])

        @self.command(name="status", pass_context=True)
        async def status(ctx) -> None:
            print(ctx)
            await ctx.channel.send("Kurwa dzialam " + ctx.author.name)

        @self.command(name="ping")
        async def ping(ctx) -> None:
            await ctx.send("pong")

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
        embed.set_thumbnail(url="https://i.imgur.com/6yk5bMu.jpeg")
        embed.add_field(name="CENA: ", value=f"**{listing.price}**", inline="false")
        embed.set_footer(
            text="by OLX Scraper", icon_url="https://i.imgur.com/hUhyNEL.jpeg"
        )
        # message = f"UWAGA - {listing.listing_name}\nCena: **{listing.price}**\nOgloszenie - {listing.link}"  # Format message
        await channel.send(embed=embed)  # Send formatted message

    # Background loop which every minute checks if there is new listng if so, post it
    # @tasks.loop(minutes=1)
    async def scrap(self) -> None:
        # Scraping process
        scraper.get_all_pages()
        for p in range(scraper.page_number):
            listings.add_unv_listings(scraper.get_listings_from_page(p))
            listings.validate_listings()

        # After validating for each listing which was not posted, call send_listing, and change bool parameter.
        for listing in listings.val_offers:
            if not listing.sent2discord:
                await self.log_listing(listing)
                await self.send_listing(listing)
                listing.sent2discord = True
                break


def main():
    with open("TOKEN.txt", "r") as f:
        TOKEN = f.read()
    intents = discord.Intents.all()
    bot = MyBot(command_prefix="-", intents=intents, self_bot=False)
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
