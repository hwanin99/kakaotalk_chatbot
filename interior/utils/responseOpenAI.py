#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import base64
import boto3
import uuid
import os
from translate import Translator
from openai import OpenAI
from PIL import Image
import json
import threading
import time
import queue as q
from fileinput import filename


def dbReset(filename):
    with open(filename, 'w') as f:
        f.write("")


def responseOpenAI(request, response_queue, filename):
    user_input = request["userRequest"]["utterance"].strip()

    # ==========================
    # 1️⃣ 상담 시작 & 상담 종료
    # ==========================
    if "상담 시작" in user_input or "상담시작" in user_input:
        dbReset(filename)
        with open(filename, "w") as f:
            f.write("START,,,")
        response_queue.put(
            textResponseFormat("상담을 시작합니다!\n먼저 이미지 URL을 입력해주세요.")
        )
        return
        
    if "상담 종료" in user_input or "상담종료" in user_input:
        dbReset(filename)
        response_queue.put(textResponseFormat("상담이 종료되었습니다.\n다음에 또 만나요!"))
        return
    
    # 항상 상태 읽기
    with open(filename) as f:
        last_update = f.read().strip()

    # 상담 시작 안 했으면 안내
    if not last_update:
        response_queue.put(textResponseFormat("상담 시작을 먼저 입력해주세요!"))
        return

    parts = last_update.split(',')
    
    # ======================
    # 2️⃣ URL 입력 단계
    # ======================
    if parts[0] == "START" and parts[1]=='' and parts[2]=='' and parts[3]=='':
        if user_input.startswith("http"):
            save_log = f"START,{user_input},,"
            with open(filename, "w") as f:
                f.write(save_log)

            response_queue.put({
                'version': '2.0',
                'template': {
                    'outputs': [
                        {'simpleImage': {
                            'imageUrl': user_input,
                            'altText': '원본 이미지'
                        }},
                        {'simpleText': {
                        'text': "이미지 URL을 저장했어요!\n이제 원하는 스타일을 입력해주세요."
                        }}
                    ] 
                }
            })
            return
        else:
            response_queue.put(textResponseFormat("올바른 URL 형식인지 확인해주세요!"))
            return

    # ======================
    # 3️⃣ 스타일 입력 단계 (생성 X)
    # ======================
    if parts[0] == 'START' and parts[1] != '' and parts[2]=='' and parts[3]=='':
        image_url = parts[1]
        style = user_input

        save_log = f"START,{image_url},{style},"
        with open(filename, "w") as f:
            f.write(save_log)

        # 버튼 출력
        response_queue.put({
            'version': '2.0',
            'template': {
                'outputs': [{'simpleText': {'text': f"'{style}' 스타일을 저장했어요!\n이제 이미지를 생성해 볼까요?"}}],
                'quickReplies': [
                    {
                        'action': 'message',
                        'label': '이미지 생성하기',
                        'messageText': '이미지 생성하기'
                    }
                ]
            }
        })
        return

    # ======================================================
    # 4️⃣ 이미지 생성하기
    # ======================================================
    if "이미지 생성하기" in user_input:
        if parts[0] != '' and parts[1] != '' and parts[2] != '':
            image_url = parts[1]
            style = parts[2]
            
            with open(filename, "w") as f:
                f.write(f"GENERATING,{image_url},{style},")

            bot_res = image_generate(image_url, style, filename)
            
            response_queue.put({
                'version': '2.0',
                'template': {
                    'outputs': [
                        {'simpleImage': {
                            'imageUrl': bot_res,
                            'altText': f"{style} 스타일의 인테리어 디자인"
                        }},
                        {'simpleText': {
                        'text': f"{style} 스타일로 변경된 디자인이에요!"
                        }}
                    ] 
                }
            })

    # ======================
    # 5️⃣ 이미지 불러오기
    # ======================
    elif "이미지 불러오기" in user_input:
        # 파일 새로 읽어오기
        with open(filename) as f:
            last_update = f.read().strip()
        
        parts = last_update.split(',')
        state = parts[0]

        if state == "DONE":
            style = parts[2]
            bot_res = parts[3]

            response_queue.put({
                'version': '2.0',
                'template': {
                    'outputs': [
                        {'simpleImage': {
                            'imageUrl': bot_res,
                            'altText': f"{style} 스타일의 인테리어 디자인"
                        }},
                        {'simpleText': {
                        'text': f"{style} 스타일로 변경된 디자인이에요!"
                        }}
                    ] 
                }
            })

            dbReset(filename)

