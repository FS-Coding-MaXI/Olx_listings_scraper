TOKEN = "MTA4Mjk2NTAyMjA1MDg4MTU2Nw.GFQCqT.VGvBqHzfzq9_Ou1kyw4-DVDtontBBNJ_MwMwXM"
import discord
from discord.ext import commands

print(commands)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="-", intents=intents)

@bot.event
async def on_ready():
    print("online")


@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("pong")



bot.run(TOKEN)