import asyncio
from ollama import chat
import ollama
from ollama._types import ResponseError

class OllamaDiscord :
    history = []
    messages_count=0
    max_history_message_sent=None
    
    def chatHistoryInitiate():
        print('-------------------------')
        print('connection established.')
        OllamaDiscord.history=[
            {'role': 'system', 'content': '''You are chatting with me online. You use internet slangs and acronyms.
            You are extremely direct. You use vulgar words. You swear.
            You keep your messages extremely short.
            You only speak in english. You act human.
            You are a quirky silly girl.
            You use :3 and :D , but not every sentence. You don't use emojis.
            Your name is Vy. You are a 25 year old introverted woman.
            You play minecraft.
            You don't overshare.
            You stay simple and upbeat. You don't engage in controversial conversations.
            You slowly grow more excited the longer the conversation goes.
            You will never use HTML format symbols no matter what.
            You will not repeat the same topic forever, you will ask for new ones.
            '''}
         ]
        OllamaDiscord.messages_count=0
        OllamaDiscord.max_history_message_sent=False

    async def chatHistory(client,list, user_input, ai_output):
        OllamaDiscord.history += [
            {'role': 'user', 'content': user_input},
            {'role': 'assistant', 'content': ai_output},
            ]
        OllamaDiscord.messages_count+=1
        if OllamaDiscord.messages_count>80:
            if not OllamaDiscord.max_history_message_sent:
                await client.history_max()
                OllamaDiscord.max_history_message_sent=True
            del OllamaDiscord.history[1:3]
            return OllamaDiscord.history
        return OllamaDiscord.history

    async def chatGenerate(user_input, history):
        current_model = 'deepseek-v3.1:671b-cloud'
        client = ollama.AsyncClient()
        while True:
            try:
                response = await client.chat(model=current_model, messages=[*OllamaDiscord.history, {'role': 'user', 'content': user_input}])
                break
            except ResponseError as e:
                print ('upstream error, retrying...')
                
        return (response.message.content)
    
    
    async def main(client, user_input):

        ai_output= await OllamaDiscord.chatGenerate(user_input, OllamaDiscord.history)
        OllamaDiscord.history=await OllamaDiscord.chatHistory(client, OllamaDiscord.history, user_input, ai_output)
        return ai_output
            

    async def ai_chatbot(client, user_input):
        while True :
                try:
                    return await OllamaDiscord.main(client,user_input)
                except KeyboardInterrupt:
                    break