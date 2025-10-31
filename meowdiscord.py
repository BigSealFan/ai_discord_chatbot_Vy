from ollamaDiscord import OllamaDiscord
import os
import sys
import discord
import asyncio
import re

class MyClient(discord.Client):

    messages_sent =""
    debounce_task = None
    startReading = None
    specific_channel_id  = None
    specific_user_id = None
    running = False

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        if message.content=='!start' and self.running==False:
            self.specific_user_id = message.author.id
            self.specific_channel_id = message.channel
            self.startReading=True
            OllamaDiscord.chatHistoryInitiate()
            self.running=True
            await self.specific_channel_id.send('connection established.')
        elif message.content[:3]!='!no':
            if self.startReading:
                if re.search(r'\bkys\b', message.content, re.IGNORECASE):
                    if message.author.id != self.specific_user_id or message.channel.id != self.specific_channel_id.id :
                        return
                    await self.specific_channel_id.send("*commits suicide and fucking dies*")
                    self.specific_channel_id=None
                    self.specific_user_id=None
                    self.running=False
                else:
                    if message.author.id != self.specific_user_id or message.channel.id != self.specific_channel_id.id :
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
                                await self.send_messages(self.fix_quotes(ai_output))
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
                        (message.find('?'),'?'),
                        (message.find(')'),')'),
                        (message.find('\n'),'\n'),
                        (message.find('"'),'"')]

            # Keep only separators that exist
            positions = [(pos, sep) for pos, sep in positions if pos != -1]

            # No separators left
            if not positions:
                if len(message) > 1 and message[1].islower():
                    message=message[:1].lower()+message[1:]
                await self.specific_channel_id.send(message)
                break

            # Pick the earliest separator
            sep_pos, sep_char = min(positions, key=lambda x: x[0])

            # Split and send
            if sep_char=='?' or sep_char=='!' or sep_char=='(' or sep_char==')' or sep_char=='"' :
                before = message[:sep_pos+1].strip()
            else:
                before = message[:sep_pos].strip()
            if len(before)>1 and before[1].islower():
                before = before[:1].lower()+before[1:]
            if sep_char=='(' and ')' in message[sep_pos + 1:]:
                after = message[sep_pos:].strip() #of ( )
            elif sep_char=='"' and '"' in message[sep_pos + 1:]:
                after = message[sep_pos:].strip() #of ( )
            else:
                after = message[sep_pos + 1:].strip()
            if before!="":
                 if sep_char=='(' and ')' in message[sep_pos + 1:]:
                     before=after[:after.find(')')+1] #of ( )
                     await self.specific_channel_id.send(before)
                     after=after[after.find(')') + 1:].strip()
                 elif sep_char=='"' and '"' in message[sep_pos + 1:]:
                     before=after[:after[1:].find('"')+2] #of " "
                     await self.specific_channel_id.send(before)
                     after=after[after[1:].find('"')+2:].strip()
                 elif (sep_char=='?' or sep_char=='!') and len(after)<4:
                    await self.specific_channel_id.send(f"{before} {after}")
                    after=""
                 else:
                    while after and after[0] in [',', '—', '.', '(', ')', '!', '?', '"']:
                        before+=after[0]
                        after=after[1:]
                    await self.specific_channel_id.send(before)
            message = after
    def fix_quotes(self,message):
        for index, character in enumerate(message):
            if character == '"':
                if message[index-1]==',':
                    message=message[:index-1]+'",'+message[index+2:]
        return message
                    
        


client = MyClient()
client.run(os.environ["VY_DISCORD_TOKEN"])