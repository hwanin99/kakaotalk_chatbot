#!/usr/bin/env python
# coding: utf-8

# # Import Module
# ---
# >* openai == 0.28.1
# >* translate == 3.6.1

# In[ ]:


import json
import openai
import threading
import time
import queue as q
import os
from translate import Translator

# OpenAI API KEY
openai.api_key = os.environ['OPENAI_API']


# In[ ]:





# # ChatGPT & DALLE-2 사용하기
# ---
# >* prompt를 받아서 ChatGPT/DALLE-2가 응답해주는 함수
#     * DALLE-2는 한국말을 이해를 잘 못하기에 Translator를 통해 한국말을 prompt로 입력하면 자동으로 영어로 번역해서 입력해주는 기능을 추가  
#     
# >* ChatGPT/DALLE-2에게 응답받은 값을 카카오톡 챗봇 형식에 맞게 json형식으로 변환

# In[ ]:


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


# In[ ]:





# # 비동기 처리
# ---
# >* 카카오톡 챗봇의 경우에는 5초간 응답이 없으면 에러가 발생
#     * DALLE-2는 응답이 5초가 넘는 경우가 대부분이기에, 이를 해결하기 위해 비동기 처리

# In[ ]:


# 응답시간 초과시 먼저 답변
def timeover():
    response = {'version': '2.0', 'template': {
        'outputs': [
            {
                'simpleText': {
                    'text': "앗 죄송합니다! 아직 생각 중이에요.\n잠시 후 아래 말풍선을 눌러주세요."
                }
            }
        ], 'quickReplies': [
            # 생각이 다 끝남? 버튼생성
            {
                'action': 'message',
                'label': '생각 다 했니?',
                'messageText': '생각 다 했니?'
            }
        ]
    }}
    return response


# In[ ]:





# # Main
# ---
# >* aws lambda를 사용하기 위해 아래와 같이 메인 함수를 사용 

# In[ ]:


# 메인 함수
def lambda_handler(event, context):
    run_flag = False
    start_time = time.time()
    # 카카오 정보 저장
    kakaorequest = json.loads(event['body'])
    # 응답 결과를 저장하기 위한 텍스트 파일 생성

    filename ="/tmp/botlog.txt"

    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("")
    else:
        print("File Exists")    

    # 답변 생성 함수 실행
    # 큐 생성(퍼스트 인, 퍼스트 아웃)
    response_queue = q.Queue()
    request_respond = threading.Thread(target=responseOpenAI, args=(kakaorequest, response_queue, filename))
    # responseOpenAI 함수를 비동기적으로 만들어서, 실행. 결과 기다리지 않고 다음줄 실행
    request_respond.start()

    # 응답이 3.5초 이내에 오면
    while(time.time() - start_time < 3.5):
        # 답변이 있으면,
        if not response_queue.empty():
            response = response_queue.get()
            run_flag = True
            break
        # 안정적인 구동을 위한 딜레이 타임 설정
        time.sleep(0.01)

    # 응답이 3.5초 이내에 오지 않으면
    if run_flag == False:
        # 생각 끝남버튼 출력함수 호출
        response = timeover()

    return{
        'statusCode':200,
        'body': json.dumps(response),
        'headers': {
            'Access-Control-Allow-Origin': '*',
        }
    }

# 답변/사진 요청 및 응답 확인 함수
def responseOpenAI(request,response_queue,filename):
    # 사용자다 버튼을 클릭하여 답변 완성 여부를 다시 봤을 시
    if '생각 다 했니?' in request["userRequest"]["utterance"]:
        # 텍스트 파일 열기
        with open(filename) as f:
            last_update = f.read()
        # 텍스트 파일 내 저장된 정보가 있을 경우
        if len(last_update.split())>1:
            kind = last_update.split()[0]
            if kind == "img":
                parts = last_update.split(' ', 2)
                kind = parts[0]
                bot_res = parts[1]
                prompt = parts[2]
                response_queue.put(imageResponseFormat(bot_res, prompt))
            else:
                bot_res = last_update[4:]
                response_queue.put(textResponseFormat(bot_res))
            dbReset(filename)

    # 이미지 생성을 요청한 경우
    elif '/img' in request["userRequest"]["utterance"]:
        dbReset(filename)
        prompt = request["userRequest"]["utterance"].replace("/img", "")
        bot_res = getImageURLFromDALLE(prompt)
        response_queue.put(imageResponseFormat(bot_res,prompt))
        save_log = "img"+ " " + str(bot_res) + " " + str(prompt)
        with open(filename, 'w') as f:
            f.write(save_log)

    # ChatGPT 답변을 요청한 경우
    elif '/ask' in request["userRequest"]["utterance"]:
        dbReset(filename)
        prompt = request["userRequest"]["utterance"].replace("/ask", "")
        bot_res = getTextFromGPT(prompt)
        response_queue.put(textResponseFormat(bot_res))

        save_log = "ask"+ " " + str(bot_res)
        with open(filename, 'w') as f:
            f.write(save_log)

    #아무 답변 요청이 없는 채팅일 경우
    else:
        # 기본 response 값
        base_response = {'version': '2.0', 'template': {'outputs': [], 'quickReplies': []}}
        response_queue.put(base_response)

def dbReset(filename):
    with open(filename, 'w') as f:
        f.write("")

