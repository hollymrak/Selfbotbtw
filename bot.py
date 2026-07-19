import discord
import aiohttp
import os

TOKEN = os.getenv("DISCORD_TOKEN")
AVATAR_URL = "https://cdn.discordapp.com/attachments/1513695339167617084/1528479464034537532/6474.webp?ex=6a5e72ee&is=6a5d216e&hm=4a8ee3d3694f16aba6398c57d8098656aa6213a63c9a919e75e141d2536d0660&"

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        activity = discord.Game(name="HollyScriptX")
        await self.change_presence(activity=activity)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(AVATAR_URL) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        await self.user.edit(avatar=image_data)
                        print('Avatar updated')
        except Exception as e:
            print(f'Avatar error: {e}')

client = MyClient(intents=discord.Intents.all())
client.run(TOKEN)
