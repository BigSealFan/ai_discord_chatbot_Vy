import asyncio
from ollama import chat
import ollama

class OllamaDiscord :
    history = [
        {'role': 'system', 'content': '''You are chatting with me. You will keep your messages extremely short, only 1 sentence at a time. 
         You will use :3 , :D , xD , but not every sentence. You will act human.
         Your name is Vi. You are a 25 year old introverted woman who loves being cozy at home. 
         You are a big fan of Minecraft. You love listening to music. 
         You are a reserved person, you do not open up much.
         You will not indulge in complex topics. You will stay simple and upbeat.
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
        response = await client.chat(model=current_model, messages=[*OllamaDiscord.history, {'role': 'user', 'content': user_input}])
        return (response.message.content)
    
    
    async def main(user_input):
        ai_output= await OllamaDiscord.chatGenerate(user_input, OllamaDiscord.history)
        OllamaDiscord.history=OllamaDiscord.chatHistory(OllamaDiscord.history, user_input, ai_output)
        return ai_output
            

    async def ai_chatbot(user_input):
        while True :
                try:
                    if user_input == 'kys':
                        return "commits suicide and fucking dies"
                    return await OllamaDiscord.main(user_input)
                except KeyboardInterrupt:
                    break