TOKEN = "MTA4Mjk2NTAyMjA1MDg4MTU2Nw.GFQCqT.VGvBqHzfzq9_Ou1kyw4-DVDtontBBNJ_MwMwXM"
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

    async def on_ready(self):
        channel = self.get_channel(1082965800400474164)
        await channel.send("I have started! ")
        self.scrap.start()

    def add_commands(self):
        @self.command(name="status", pass_context=True)
        async def status(ctx):
            print(ctx)
            await ctx.channel.send("Kurwa dzialam " + ctx.author.name)

        @self.command(name="ping")
        async def ping(ctx):
            await ctx.send("pong")

    async def send_listing(self, listing) -> None:
        channel = self.get_channel(1083725146080149524)
        message = f"UWAGA - {listing.listing_name}\nCena: **{listing.price}**\nOgloszenie - {listing.link}"
        await channel.send(message)

    @tasks.loop(minutes=1)
    async def scrap(self):
        scraper.get_all_pages()
        for p in range(scraper.page_number):
            listings.add_unv_listings(scraper.get_listings_from_page(p))
            listings.validate_listings()
        for listing in listings.val_offers:
            if not listing.sent2discord:
                await self.send_listing(listing)
                listing.sent2discord = True


def main():
    intents = discord.Intents.all()
    bot = MyBot(command_prefix="-", intents=intents, self_bot=False)

    bot.run(TOKEN)


if __name__ == "__main__":
    main()
