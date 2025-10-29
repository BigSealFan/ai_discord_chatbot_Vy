from ollamaDiscord import OllamaDiscord
import os
import sys
import discord
from discord.ext import commands

class MyClient(discord.Client):

    async def on_ready(self):
        print('Logged on as', self.user, '\n')

    async def on_message(self, message):
        specific_user_id = 507212584634548254
        if message.author.id != specific_user_id :
            return
        
        ai_output = await OllamaDiscord.ai_chatbot(message.content)
        await message.channel.send(ai_output)
        if ai_output == "commits suicide and fucking dies":
            await self.close()
            sys.exit()

client = MyClient()
client.run(os.environ["VY_DISCORD_TOKEN"])



