# pip install ollama

# from ollama import chat
# from ollama import ChatResponse

# response: ChatResponse = chat(model='qwen2.5-coder:7b', messages=[
#   {
#     'role': 'user',
#     'content': 'Why is the sky blue?',
#   },
# ])
# print(response['message']['content'])
# # or access fields directly from the response object
# print(response.message.content)

import asyncio
from ollama import AsyncClient

async def chat():
  message = {'role': 'user', 'content': 'Write a button class in wxImageButtonFrame and in Qt, use C++17 with lambda'}
  async for part in await AsyncClient().chat(model='qwen2.5-coder:7b', messages=[message], stream=True):
    print(part['message']['content'], end='', flush=True)

asyncio.run(chat())