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
        if (message.content=='!start' and self.running==False) or message.content=='!forcestart':
            self.specific_user_id = message.author.id
            self.specific_channel_id = message.channel
            self.startReading=True
            OllamaDiscord.chatHistoryInitiate()
            self.running=True
            await self.specific_channel_id.send(f"<@{message.author.id}> connection established.")
        elif message.content[:3]!='!no':
            if self.startReading:
                if re.search(r'\bkys\b', message.content, re.IGNORECASE):
                    if message.author.id != self.specific_user_id or message.channel.id != self.specific_channel_id.id :
                        return
                    await self.specific_channel_id.send("*commits suicide and fucking dies*")
                    print('-------------------------')
                    print("connection disconnected.")
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
                                ai_output = await OllamaDiscord.ai_chatbot(self,self.messages_sent)
                                print('-------------------------')
                                print(ai_output)
                                await self.send_messages(self.fix_quotes(ai_output))
                                self.messages_sent = "" 
                            except asyncio.CancelledError:
                                pass

                    self.debounce_task = asyncio.create_task(send_the_sum())


                    
    positions=[]
    chunks=[('(',')'),('"','"'),('“','”'),('*','*')]
    before=None
    after=None

    def initiate_list(self,message):
        self.positions = [(message.find(','), ','), 
                            (message.find('—'), '—'), 
                            (message.find('.'), '.'),
                            (message.find('('),'('),
                            (message.find('!'),'!'),
                            (message.find('?'),'?'),
                            (message.find(')'),')'),
                            (message.find('\n'),'\n'),
                            (message.find('"'),'"'),
                            (message.find('“'),'“'), #beginning
                            (message.find('”'),'”'), #end
                            (message.find('*'),'*')
                            ]
        self.positions = [(pos, sep) for pos, sep in self.positions if pos != -1] #only take existing separators
    
    def lowercase_uppercase(self,message): 
         if len(message) > 1 and message[1].islower(): #if the first Word isn't all UPPERCASE, make it all lowercase
                    message=message[:1].lower()+message[1:]
         return message

    async def send_messages(self,message):
        while message and message!="":
            
            self.initiate_list(message)
            
            if not self.positions or self.positions==[]: #no separators
                await self.specific_channel_id.send(self.lowercase_uppercase(message))
                message=None
                break

            fpos, fchar = min(self.positions, key=lambda x: x[0]) #first separator and its position

            if any(fchar==chunk1 and chunk2 in message[fpos+1:] for chunk1, chunk2 in self.chunks) and len(message)>1: #if a chunk exists
                fchar2 = next((chunk2 for chunk1, chunk2 in self.chunks if chunk1 == fchar),) #find the appropriate end of chunk
                before, after, rest = self.chunk(message, fchar, fchar2)
                if self.lowercase_uppercase(before.strip()): #to avoid empty messages 
                    await self.specific_channel_id.send(self.lowercase_uppercase(before.strip()))
                if self.lowercase_uppercase(after.strip()):
                    await self.specific_channel_id.send(self.lowercase_uppercase(after.strip()))
                message=rest
                continue

            before, after = self.split(message, fchar)
            if self.lowercase_uppercase(before.strip()):
                await self.specific_channel_id.send(self.lowercase_uppercase(before.strip()))
            message=after.strip()



    def chunk(self,message, sep1, sep2): #returns before chunk between 2 separators, and after
         sep1_index=message.find(sep1) 
         sep2_index=message.find(sep2, sep1_index + 1) #include the second sep in the chunk

         while sep2_index+1<len(message) and any(sep==message[sep2_index+1] for pos, sep in self.positions) : #if next character is also a separator
              sep2_index+=1 #include it in chunk

         return message[:sep1_index].strip(), message[sep1_index:sep2_index+1].strip(), message[sep2_index+1:].strip()
    
    def split(self,message, sep):
         if sep=='—' or sep==',' or sep=='.'or sep=='\n': #don't include those in the visible message
            sep_index=message.find(sep) 
         else:
            sep_index=message.find(sep) +1 #include the rest

         three_points=False
         while sep_index+1<len(message) and any(sepp==message[sep_index+1] for pos, sepp in self.positions): #if next character is also a separator
              sep_index+=1 #include it in split
              if not three_points and sep=='.' or sep=='!' or sep=='?': #in case of spams like !!! ??? ...
                 if sep=='.': #look at beginning of the function
                     sep_index+=1
                 sep_index+=1
                 three_points=True
         if '?!' in message or '!?' in message: #it only does +1 for one of them
            sep_index+=1
         
         return message[:sep_index].strip(), message[sep_index+1:].strip()

    def fix_quotes(self,message): #fix for sometimes when the ai puts the comma before the end of quotes
        for index, character in enumerate(message):
            if character=='"':
                if message[index-1]==',':
                    message=message[:index-1]+'",'+message[index+2:]
            if character=='”':
                if message[index-1]==',':
                    message=message[:index-1]+'”,'+message[index+2:]
        return message
    
    async def history_max(self):
        await self.specific_channel_id.send("[chat history reached max. removing earlier messages.]")
                    
        


client = MyClient()
client.run(os.environ["VY_DISCORD_TOKEN"])