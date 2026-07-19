import discord
from discord.ext import commands
import aiohttp
import os

TOKEN = os.getenv("DISCORD_TOKEN")
INVITE_LINK = "https://discord.gg/hsx"
AVATAR_URL = "https://cdn.discordapp.com/attachments/1513695339167617084/1528479464034537532/6474.webp?ex=6a5e72ee&is=6a5d216e&hm=4a8ee3d3694f16aba6398c57d8098656aa6213a63c9a919e75e141d2536d0660&"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)

class InviteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        button = discord.ui.Button(label="Join Discord", url=INVITE_LINK)
        self.add_item(button)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} is online')
    
    activity = discord.Game(name="HollyScriptX")
    await bot.change_presence(activity=activity)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(AVATAR_URL) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    await bot.user.edit(avatar=image_data)
                    print('Avatar updated')
    except Exception as e:
        print(f'Avatar error: {e}')

@bot.command()
async def invite(ctx):
    view = InviteView()
    await ctx.send("Join our discord!", view=view)

@bot.command()
async def status(ctx):
    embed = discord.Embed(
        title="HollyScriptX",
        description="discord.gg/hsx",
        color=discord.Color.blue()
    )
    embed.set_image(url=AVATAR_URL)
    view = InviteView()
    await ctx.send(embed=embed, view=view)

bot.run(TOKEN)
