from ollamaDiscord import OllamaDiscord
import os
import sys
import discord
import asyncio
import re
import ast
from pathlib import Path
import json
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
                await self.specific_channel.send("Timed out.")
                return
            
            message = message.content.strip().lower()
            if message in ('yes','y'):
                self.waiting_for_confirmation=False
                return True
            if message in ('no','n'):
                self.waiting_for_confirmation=False
                return
            await self.specific_channel.send("```only respond with Yes or No```")

    async def commands (self, message):
        msg = message.content[1:].lower()
        index=msg.find(' ') +1
        if msg.startswith("help"):
            await self.specific_channel.send('```!start``` to start new conversation```!no [whatever u wanna say]``` ignores anything u write in that message```!save [name]``` to save your chat history as [name]```!load [name]``` to load your chat history of [name]```!reset```to reset the chat history and start a new conversation```!end``` to end current conversation')
            if self.is_admin(message): #commands for only admin accounts
                await self.specific_channel.send('```!delete <file_name>``` to delete a save file ```!changec <channel_id>``` to move current conversation to another channel without interrupting ```!changeu <user_id>``` to move current conversation to another user ```!addadmin <user_id>``` pretty self explanatory ```!deladmin <user_id>``` removes the pretty self explanatory')
            return
        if msg.startswith("start"):
            await self.specific_channel.send("```conversation already started```")
            return
        
        elif msg.startswith("forcestart"):
            if not self.is_admin(message):
                await self.specific_channel.send("```you are not admin >:(```")
                return
            self.specific_user_id = message.author.id
            self.specific_channel = message.channel
            OllamaDiscord.chatHistoryInitiate()
            self.running=True
            await self.specific_channel.send(f'<@{message.author.id}> connection established. <!help> for list of commands')
            return
            
        if self.running:
             if message.author.id == self.specific_user_id and message.channel.id == self.specific_channel.id :
                if msg.startswith("end"):
                    await self.specific_channel.send("```connection disconnected.```")
                    print('-------------------------')
                    print("connection disconnected.")
                    self.specific_channel=None
                    self.specific_user_id=None
                    self.running=False
                    return
            
                elif msg.startswith("reset"):
                    OllamaDiscord.chatHistoryInitiate()
                    await self.specific_channel.send(f"<@{self.specific_user_id}> connection reset.")
                    print('-------------------------')
                    print("connection reset.")
                    return
            
                elif msg.startswith("save"):
                    if msg=="save":
                        await self.specific_channel.send("```please specify the name of the save file : !save name_of_file```")
                        return
                    name=msg[index:].replace(" ","_").lower().strip() #name case insensitive and no spaces
                    with open("saves/logs.txt", "r", encoding="utf-8") as file: 
                        for line in file: 
                            if name==line.lower().strip(): #if exact match only
                                await self.specific_channel.send("```this save file already exists. please choose another name```")
                                return
                        file_name=f"saves/{name}.txt" 
                    with open(file_name, "w", encoding="utf-8") as file:
                            file.write(str(OllamaDiscord.history)) #put the chat history in text file
                    with open("saves/logs.txt", "a", encoding="utf-8") as file:
                            file.write(f"\n{name}") #add the name of the text file in the logs for easier check
                    await self.specific_channel.send(f'```save file "{name}" successfully saved!```')
                    return

                elif msg.startswith("load"):
                    if msg=="load":
                        await self.specific_channel.send("```please specify the name of the load file : !load name_of_file```")
                        return
                    await self.specific_channel.send("```are you sure you want to load ? any unsaved conversation will be gone. answer Yes or No```") 
                    if not await self.are_you_sure(message.author.id, message.channel.id):
                        await self.specific_channel.send("```loading process cancelled```")
                        return
                    name=msg[index:].replace(" ","_").lower().strip() #name case insensitive and no spaces
                    with open("saves/logs.txt", "r", encoding="utf-8") as file:
                        found=None 
                        for line in file: 
                            if name==line.lower().strip(): #if exact match only
                                found=True
                        if not found:
                            await self.specific_channel.send("```this load file doesn't exist. please choose a valid name```")
                            return   
                    file_name=f"saves/{name}.txt" 
                    with open(file_name, "r", encoding="utf-8") as file:
                        OllamaDiscord.history = ast.literal_eval(file.read())
                    await self.specific_channel.send(f'load file "{name}" successfully loaded!')
                    return
                
             if msg.startswith("delete"):
                if not self.is_admin(message):
                    await self.specific_channel.send("```you are not admin >:(```")
                    return
                if msg=="delete":
                    await self.specific_channel.send("```please specify the name of the file u wish to delete : !delete name_of_file```")
                    return
                name=msg[index:].replace(" ","_").lower().strip() #name case insensitive and no spaces
                await self.specific_channel.send(f'```are you sure you want to delete "{name}" ? the file will be permanently lost. answer Yes or No```') 
                if not await self.are_you_sure(message.author.id, message.channel.id):
                    await self.specific_channel.send("```deleting process cancelled```")
                    return
                with open("saves/logs.txt", "r+", encoding="utf-8") as file:
                    lines = file.readlines() #stock all lines
                    found=None 
                    file.seek(0) #go to beginning
                    file.truncate() #nuke everything
                    for line in lines: 
                        if name==line.lower().strip(): #if exact match only
                            found=True
                            continue #dont rewrite the targetted line
                        file.write(line) #rewrite everything
                    if not found:
                        await self.specific_channel.send("```this save file doesn't exist. please choose a valid name```")
                        return
                file_name=f"saves/{name}.txt" 
                Path(file_name).unlink()
                await self.specific_channel.send(f'```save file "{name}" successfully deleted!```')
                return
            
             elif msg.startswith("addadmin"):
                if not self.is_admin(message):
                    await self.specific_channel.send("```you are not admin >:(```")
                    return
                if msg=="addadmin":
                    await self.specific_channel.send("```please specify the ID of the user to be added as admin : !addadmin user_id```")
                    return
                user_id=int(msg[index:].replace(" ","_").strip()) # no spaces
                if user_id in self.admins:
                    await self.specific_channel.send(f'```user {user_id} is already admin```')
                    return
                else:
                    self.admins.append(user_id)
                    with open("admins.json", "w") as f:
                        json.dump(self.admins, f)
                    await self.specific_channel.send(f'```added {user_id} as admin!```')
                    return
        
             elif msg.startswith("deladmin"):
                if not self.is_admin(message):
                    await self.specific_channel.send("```you are not admin >:(```")
                    return
                if msg=="deladmin":
                    await self.specific_channel.send("```please specify the ID of the user to be removed from admin : !deladmin user_id```")
                    return
                user_id=int(msg[index:].replace(" ","_").strip()) # no spaces
                if user_id in self.admins:
                    self.admins.remove(user_id)
                    with open("admins.json", "w") as f:
                        json.dump(self.admins, f)
                    await self.specific_channel.send(f'```user {user_id} removed from admin```')
                    return
                else:
                    await self.specific_channel.send(f"```user {user_id} isn't an admin```")
                    return
            
             elif msg.startswith("changeu"):
                if not self.is_admin(message):
                    await self.specific_channel.send("```you are not admin >:(```")
                    return
                self.specific_user_id=int(msg[index:].strip())
                await self.specific_channel.send(f'user successfully changed to <@{self.specific_user_id}>')
                return
            
             elif msg.startswith("changec"):
                if not self.is_admin(message):
                    await self.specific_channel.send("```you are not admin >:(```")
                    return
                temporary_channel=self.specific_channel
                self.specific_channel= await self.fetch_channel(msg[index:].strip())
                await temporary_channel.send(f"```conversation successfully moved to channel : {self.specific_channel.name}```")
                await self.specific_channel.send(f"```conversation successfully moved to this channel```")
                return
                    
        if msg.startswith("no"):
            return
        await self.specific_channel.send("```not a valid command```")
        return
                    


    async def on_ready(self):
        print('Logged on as', self.user)
        self.initiate_admins()

    async def on_message(self, message):
        if not message.guild: #ignore all DMs
            return
        if self.waiting_for_confirmation:
            return
        if (message.content=='!start' and self.running==False) or message.content=='!forcestart':
             if not self.running:
                    self.specific_user_id = message.author.id
                    self.specific_channel = message.channel
                    OllamaDiscord.chatHistoryInitiate()
                    self.running=True
                    await self.specific_channel.send(f'<@{message.author.id}> connection established. <!help> for list of commands')
                    return
        if self.running:
            if (message.author.id != self.specific_user_id or message.channel.id != self.specific_channel.id) and not self.is_admin(message) :
                return
            if message.content[0]=='!':
                await self.commands(message)
            else :
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
os.startfile("Discord Canary.lnk")
os.startfile("Ollama.lnk")
client.run(os.environ["VY_DISCORD_TOKEN"])