# pip install -r requirements.txt

from ollamaDiscord import OllamaDiscord
import os
import discord
import asyncio
import re
import json
from commands import Commands
class MyClient(discord.Client):

    messages_sent =""
    debounce_task = None
    specific_channel  = None
    specific_user_id = None
    running = False
    waiting_for_confirmation=False
    admins = [] #admin accounts

    def initiate_admins(self):
        file_path = "admins.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                self.admins = json.load(f)
        else:
            self.admins = []

    def is_admin(self, message): #checks if current user is admin or not
        return message.author.id in self.admins

    async def are_you_sure(self, user_id, channel_id):
        self.waiting_for_confirmation=True
        def check(m) : return (m.author.id == user_id and m.channel.id == channel_id)
        while True:
            try:
                message = await self.wait_for("message", check=check, timeout=30)
            except asyncio.TimeoutError:
                await self.specific_channel.send("```Timed out.```")
                self.waiting_for_confirmation=False
                return
            
            message = message.content.strip().lower()
            if message in ('yes','y'):
                await asyncio.sleep(2) 
                self.waiting_for_confirmation=False
                return True
            if message in ('no','n'):
                await asyncio.sleep(2) 
                self.waiting_for_confirmation=False
                return
            await self.specific_channel.send("```only respond with Yes or No```")

    async def on_ready(self):
        print('Logged on as', self.user)
        self.initiate_admins()

    async def on_message(self, message):
        if not message.guild: #ignore all DMs
            return
        elif self.waiting_for_confirmation:
            return
        elif (message.content=='!start' and self.running==False) or message.content=='!forcestart':
             if not self.running:
                    self.specific_user_id = message.author.id
                    self.specific_channel = message.channel
                    OllamaDiscord.chatHistoryInitiate()
                    self.running=True
                    await self.specific_channel.send(f'<@{message.author.id}> connection established. <!help> for list of commands')
                    return
        elif self.running:
            if (message.author.id != self.specific_user_id or message.channel.id != self.specific_channel.id):
                return
            if message.content[0]=='!':
                await Commands.commands(self,message)
                return
            else :
                if not self.messages_sent:
                    self.messages_sent=message.content
                else:
                    self.messages_sent+=f" . {message.content}"
                if self.debounce_task and not self.debounce_task.done():
                    self.debounce_task.cancel()

                self.debounce_task = asyncio.create_task(self.send_the_sum())

    async def send_the_sum(self):
        try:
            await asyncio.sleep(2)
            ai_output = await OllamaDiscord.ai_chatbot(self,self.messages_sent)
            print('-------------------------')
            print(ai_output)
            await self.send_messages(self.fix_quotes(ai_output))
            self.messages_sent = "" 
        except asyncio.CancelledError:
            pass
                    
    positions=[]
    chunks=[('(',')'),('"','"'),('“','”'),('*','*')]
    before=None
    after=None

    def initiate_list(self,message):
        message = message.replace('\\n', '\n') #transforms fake \n into real ones
        separators = [',','—','.','(','!','?',')','"','“','”','*','\n', '…']
        self.positions = []
        for sep in separators:
            for match in re.finditer(re.escape(sep), message):
                pos = match.start()
                if (
                    sep == '.' and pos < len(message)-1 and message[pos + 1].isalpha() # Skip dots inside words (like "hell.o" or "v1.2")
                ):
                    continue
                self.positions.append((pos, sep))

        # sort positions by order of appearance
        self.positions.sort(key=lambda x: x[0])


    def lowercase_uppercase(self,message): 
         if len(message) > 1 and message[1].islower(): #if the first Word isn't all UPPERCASE, make it all lowercase
                    message=message[:1].lower()+message[1:]
         return message

    async def send_messages(self,message):
        while message and message!="":
            
            self.initiate_list(message)
            
            if not self.positions or self.positions==[]: #no separators
                if self.lowercase_uppercase(message.strip())!='n':
                    await self.specific_channel.send(self.lowercase_uppercase(message))
                message=None
                break

            fpos, fchar = self.positions[0] #first separator and its position

            if any(fchar==chunk1 and chunk2 in message[fpos+1:] for chunk1, chunk2 in self.chunks) and len(message)>1: #if a chunk exists
                fchar2 = next((chunk2 for chunk1, chunk2 in self.chunks if chunk1 == fchar),None) #find the appropriate end of chunk
                before, after, rest = self.chunk(message, fchar, fchar2)
                if self.lowercase_uppercase(before.strip()): #to avoid empty messages 
                    await self.specific_channel.send(self.lowercase_uppercase(before.strip()))
                if self.lowercase_uppercase(after.strip()):
                    await self.specific_channel.send(self.lowercase_uppercase(after.strip()))
                message=rest
                continue

            before, after = self.split(message, fchar, fpos)
            if self.lowercase_uppercase(before.strip()) and self.lowercase_uppercase(before.strip())!='n':
                await self.specific_channel.send(self.lowercase_uppercase(before.strip()))
            message=after.strip()


    def chunk(self,message, sep1, sep2): #returns before chunk between 2 separators, and after
         sep1_index=message.find(sep1) 
         sep2_index=message.find(sep2, sep1_index + 1) #include the second sep in the chunk

         while sep2_index+1<len(message) and any(sep==message[sep2_index+1] for pos, sep in self.positions) : #if next character is also a separator
              sep2_index+=1 #include it in chunk

         return message[:sep1_index].strip(), message[sep1_index:sep2_index+1].strip(), message[sep2_index+1:].strip()
    
    def split(self,message, sep, sep_index):
         if not(sep=='—' or sep==',' or sep=='.'or sep=='\n'): #don't include those in the visible message
            sep_index=message.find(sep) +1 #include the rest

         three_points=False
         var=0
         chunk_first_chars = [chunk1 for chunk1, chunk2 in self.chunks]
         while sep_index+1<len(message) and any(sepp==message[sep_index+1] for pos, sepp in self.positions) and message[sep_index+1] not in chunk_first_chars:
          #if next character is also a separator
              sep_index+=1 #include it in split
              if not three_points and (sep=='.' or sep=='!' or sep=='?'): #in case of spams like !!! ??? ...
                 if sep=='.': #look at beginning of the function
                     sep_index+=1
                     var=1
                 sep_index+=1
                 three_points=True
         if '?!' in message or '!?' in message: #it only does +1 for one of them
            sep_index+=1
         
         return message[:sep_index].strip(), message[sep_index+1-var:].strip()

    def fix_quotes(self,message): #fix for sometimes when the ai puts the comma before the end of quotes
        i=0
        for index, character in enumerate(message):
            if character=='"' and index>0:
                i+=1
                if message[index-1]==',' and  i%2==0:
                    message=message[:index-1]+'",'+message[index+2:]
            if character=='”':
                if message[index-1]==',':
                    message=message[:index-1]+'”,'+message[index+2:]
        return message
    
    async def history_max(self):
        await self.specific_channel.send("[chat history reached max. removing earlier messages.]")
                    
        

client = MyClient()
client.run(os.environ["VY_DISCORD_TOKEN"])