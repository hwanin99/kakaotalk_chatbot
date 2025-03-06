'''
openai == 0.28.1
translate == 3.6.1
'''

import os
import openai
from translate import Translator

# OpenAI API KEY
# openai.api_key = os.environ['OPENAI_API'] #환경변수
openai.api_key = 'Your_OPENAI_API_KEY'

# ChatGPT에게 질문/답변 받기
def getTextFromGPT(prompt):
    messages_prompt = [{"role": "system", "content": 'You are a thoughtful assistant. Respond to all input in 25 words and answer in korea'}]
    messages_prompt += [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages_prompt)
    message = response["choices"][0]["message"]["content"]
    return message

# DALLE-2에게 질문/그림 URL 받기
def getImageURLFromDALLE(prompt):
    translator = Translator(from_lang='ko',to_lang='en')
    prompt = translator.translate(prompt) # prompt를 영어로 번역
    response = openai.Image.create(prompt=prompt,n=1,size="512x512")
    image_url = response['data'][0]['url']
    return image_url

# 카카오채널에 gpt의 메세지 전송
def textResponseFormat(bot_response):
    response = {'version': '2.0', 'template': {
        'outputs': [{'simpleText': {'text': bot_response}}], 'quickReplies': []}}
    return response

# 카카오채널에 dalle 이미지 전송
def imageResponseFormat(bot_response, prompt):
    output_text = prompt + "내용에 관한 이미지 입니다"
    response = {'version': '2.0', 'template': {
        'outputs': [{'simpleImage': {'imageUrl': bot_response, 'altText': output_text}}], 'quickReplies': []}}
    return response
