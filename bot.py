import discord
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} is online')
    await bot.change_presence(activity=discord.Game(name="HollyScriptX"))

@bot.command()
async def invite(ctx):
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Join Discord", url="https://discord.gg/hsx"))
    await ctx.send("Join our discord!", view=view)

bot.run(TOKEN)
