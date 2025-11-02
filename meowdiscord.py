from ollamaDiscord import OllamaDiscord
import os
import sys
import discord
import asyncio
import re
import ast
class MyClient(discord.Client):

    messages_sent =""
    debounce_task = None
    specific_channel  = None
    specific_user_id = None
    running = False

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        if (message.content=='!start' and self.running==False) or message.content=='!forcestart':
            self.specific_user_id = message.author.id
            self.specific_channel = message.channel
            OllamaDiscord.chatHistoryInitiate()
            self.running=True
            await self.specific_channel.send(f'<@{message.author.id}> connection established. <!help> for list of commands')
        
        elif message.content[:5]=='!help' and self.running:
            await self.specific_channel.send('```!start``` to start new conversation```!no [whatever u wanna say]``` ignores anything u write in that message```!save [name]``` to save your chat history as [name]```!load [name]``` to load your chat history of [name]```!end``` to end current conversation')

        elif message.content=='!save' and self.running:
            await self.specific_channel.send("please specify the name of the save file : !save name_of_file")

        elif message.content=='!load' and self.running:
            await self.specific_channel.send("please specify the name of the load file : !load name_of_file")

        elif message.content[:5]=='!save' and self.running:
            name=message.content[6:].replace(" ","_").lower().strip() #name case insensitive and no spaces
            with open("saves/logs.txt", "r") as file: 
                for line in file: 
                    if name==line.lower().strip(): #if exact match only
                        await self.specific_channel.send("this save file already exists. please choose another name")
                        return

                file_name=f"saves/{name}.txt" 
                with open(file_name, "w") as file:
                    file.write(str(OllamaDiscord.history)) #put the chat history in text file
                with open("saves/logs.txt", "a") as file:
                    file.write(f"\n{name}") #add the name of the text file in the logs for easier check
                await self.specific_channel.send(f'save file "{name}" successfully saved!')

        elif message.content[:5]=='!load' and self.running: 
             name=message.content[6:].replace(" ","_").lower().strip() #name case insensitive and no spaces
             with open("saves/logs.txt", "r") as file:
                found=None 
                for line in file: 
                    if name==line.lower().strip(): #if exact match only
                        found=True
                if not found:
                 await self.specific_channel.send("this load file doesn't exist. please choose a valid name")
                 return
                    
                file_name=f"saves/{name}.txt" 
                with open(file_name, "r") as file:
                    OllamaDiscord.history = ast.literal_eval(file.read())
                await self.specific_channel.send(f'load file "{name}" successfully loaded!')
            
        elif message.content=='!end' and self.running:
                if message.author.id != self.specific_user_id or message.channel.id != self.specific_channel.id :
                    return
                await self.specific_channel.send("connection disconnected.")
                print('-------------------------')
                print("connection disconnected.")
                self.specific_channel=None
                self.specific_user_id=None
                self.running=False

        elif message.content[:3]!='!no' and self.running:
            if message.author.id != self.specific_user_id or message.channel.id != self.specific_channel.id :
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
                await self.specific_channel.send(self.lowercase_uppercase(message))
                message=None
                break

            fpos, fchar = self.positions[0] #first separator and its position

            if any(fchar==chunk1 and chunk2 in message[fpos+1:] for chunk1, chunk2 in self.chunks) and len(message)>1: #if a chunk exists
                fchar2 = next((chunk2 for chunk1, chunk2 in self.chunks if chunk1 == fchar),) #find the appropriate end of chunk
                before, after, rest = self.chunk(message, fchar, fchar2)
                if self.lowercase_uppercase(before.strip()): #to avoid empty messages 
                    await self.specific_channel.send(self.lowercase_uppercase(before.strip()))
                if self.lowercase_uppercase(after.strip()):
                    await self.specific_channel.send(self.lowercase_uppercase(after.strip()))
                message=rest
                continue

            before, after = self.split(message, fchar, fpos)
            if self.lowercase_uppercase(before.strip()):
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
         while sep_index+1<len(message) and any(sepp==message[sep_index+1] for pos, sepp in self.positions): #if next character is also a separator
              sep_index+=1 #include it in split
              if not three_points and (sep=='.' or sep=='!' or sep=='?'): #in case of spams like !!! ??? ...
                 if sep=='.': #look at beginning of the function
                     sep_index+=1
                     var=1
                 sep_index+=1
                 three_points=True
         if '?!' in message or '!?' in message: #it only does +1 for one of them
            sep_index+=1
         if sep=='\n': #2 char long
            var=-1
         
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