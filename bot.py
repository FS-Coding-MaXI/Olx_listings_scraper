import discord
from discord.ext import commands


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

    async def on_ready(self) -> None:
        channel = self.get_channel(self.LOG_CHANNEL)
        await channel.send("I have started! ")
        # self.scrap.start()
        # await self.scrap()

    def add_commands(self):
        # @self.command(name="test_list", pass_context=True)
        # async def test_list(ctx) -> None:
        #     self.send_listing(listings.val_offers[0])

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
    async def send_new_listing(self, ls) -> None:

        # After validating listing which was not posted, call send_listing, and change bool parameter.
        await self.log_listing(ls)
        await self.send_listing(ls)
        ls.sent2discord = True
