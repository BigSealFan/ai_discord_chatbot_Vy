from ollamaDiscord import OllamaDiscord
import ast
from pathlib import Path
import json

class Commands:
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
                    if msg=="changeu":
                        await self.specific_channel.send("```please specify the user to change to```")
                        return
                    self.specific_user_id=int(msg[index:].strip())
                    await self.specific_channel.send(f'user successfully changed to <@{self.specific_user_id}>')
                    return
                
                elif msg.startswith("changec"):
                    if not self.is_admin(message):
                        await self.specific_channel.send("```you are not admin >:(```")
                        return
                    if msg=="changec":
                        await self.specific_channel.send("```please specify the channel to change to```")
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