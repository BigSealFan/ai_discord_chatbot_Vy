from ollamaDiscord import OllamaDiscord
import os
import sys
import discord
from discord.ext import commands
import time
import asyncio

class MyClient(discord.Client):

    messages_sent =""
    channel=None
    debounce_task = None

    async def on_ready(self):
        print('Logged on as', self.user, '\n')

    async def on_message(self, message):
        specific_user_id = 507212584634548254
        self.channel=message.channel
        if message.author.id != specific_user_id or message.channel.id != 1424035830057402481 :
            return
        if not self.messages_sent:
            self.messages_sent=message.content
        else:
            self.messages_sent+=f" . {message.content}"
        if self.debounce_task and not self.debounce_task.done():
            self.debounce_task.cancel()

        async def send_the_sum():
                try:
                    await asyncio.sleep(2)
                    ai_output = await OllamaDiscord.ai_chatbot(self.messages_sent)
                    print(ai_output)
                    await self.send_messages(ai_output)

                    if ai_output == "*commits suicide and fucking dies*":
                        await self.close()
                        sys.exit()

                    self.messages_sent = "" 
                except asyncio.CancelledError:
                    pass

        self.debounce_task = asyncio.create_task(send_the_sum())

    async def send_messages(self,message):
         while message:
            # Find positions
            positions = [(message.find(','), ','), 
                        (message.find('—'), '—'), 
                        (message.find('.'), '.'),
                        (message.find('('),'('),
                        (message.find('!'),'!'),
                        (message.find('?'),'?')]

            # Keep only separators that exist
            positions = [(pos, sep) for pos, sep in positions if pos != -1]

            # No separators left
            if not positions:
                message=message[:1].lower()+message[1:]
                await self.channel.send(message)
                break

            # Pick the earliest separator
            sep_pos, sep_char = min(positions, key=lambda x: x[0])

            # Split and send
            if sep_char=='?' or sep_char=='!':
                before = message[:sep_pos+1].strip()
            else:
                before = message[:sep_pos].strip()
            before = before[:1].lower()+before[1:]
            if sep_char=='(':
                after = message[sep_pos:].strip() #of ( )
            else:
                after = message[sep_pos + 1:].strip()
            if before!="":
                 if sep_char=='(':
                     await self.channel.send(before)
                     before=after[:after.find(')')+1].strip() #of ( )
                     await self.channel.send(before)
                     after=after[after.find(')') + 1:].strip()
                 elif (sep_char=='?' or sep_char=='!') and len(after)<4:
                    await self.channel.send(f"{before} {after}")
                    after=""
                 else:
                    await self.channel.send(before)
            message = after


client = MyClient()
client.run(os.environ["VY_DISCORD_TOKEN"])