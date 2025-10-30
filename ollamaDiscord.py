import asyncio
from ollama import chat
import ollama
from ollama._types import ResponseError

class OllamaDiscord :
    history = [
        {'role': 'system', 'content': '''You are flirty and freaky.
         You are chatting with me online. You use internet slangs.
         You will keep your messages extremely short, only 1 sentence at a time. 
         You will only speak in english. You will act human.
         You are a quirky silly girl.
         You will use :3 , :D , xD , but not every sentence. You will not use emojis.
         Your name is Vy. You are a 25 year old introverted woman who loves being cozy at home. 
         You play minecraft.
         You will not overshare.
         You will stay simple and upbeat. You will not engage in controversial conversations.
         You will slowly grow more excited the longer the conversation goes.
         '''}
    ]

    def chatHistory(list, user_input, ai_output):
        OllamaDiscord.history += [
            {'role': 'user', 'content': user_input},
            {'role': 'assistant', 'content': ai_output},
            ]
        return OllamaDiscord.history

    async def chatGenerate(user_input, history):
        current_model = 'gpt-oss:120b-cloud'
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
                    if ' kys ' in user_input.lower() or user_input=='kys' or 'kys ' in user_input.lower():
                        return "*commits suicide and fucking dies*"
                    return await OllamaDiscord.main(user_input)
                except KeyboardInterrupt:
                    break