import asyncio
from ollama import chat
import ollama
from ollama._types import ResponseError

class OllamaDiscord :
    history = []
    messages_count=0
    
    def chatHistoryInitiate():
        print('done')
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

    def chatHistory(list, user_input, ai_output):
        OllamaDiscord.history += [
            {'role': 'user', 'content': user_input},
            {'role': 'assistant', 'content': ai_output},
            ]
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
    
    
    async def main(user_input):

        ai_output= await OllamaDiscord.chatGenerate(user_input, OllamaDiscord.history)
        OllamaDiscord.history=OllamaDiscord.chatHistory(OllamaDiscord.history, user_input, ai_output)
        return ai_output
            

    async def ai_chatbot(user_input):
        while True :
                try:
                    return await OllamaDiscord.main(user_input)
                except KeyboardInterrupt:
                    break