import discord
import os

TOKEN = os.getenv("DISCORD_TOKEN")

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.change_presence(activity=discord.Game(name="HollyScriptX"))

client = MyClient(intents=discord.Intents.all())
client.run(TOKEN)
