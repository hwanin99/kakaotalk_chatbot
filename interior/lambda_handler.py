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

from utils.asynchronous import timeover
from utils.image_generator import chatgpt, upload_to_s3, image_generate
from utils.kakao_response import textResponseFormat, imageResponseFormat
from utils.responseOpenAI import dbReset, responseOpenAI


def lambda_handler(event, context):
    run_flag = False
    start_time = time.time()

    # 카카오 정보 저장
    kakaorequest = json.loads(event['body'])

    # 응답 결과 저장 파일
    filename = "/tmp/botlog.txt"
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("")
    else:
        print("File Exists")

    # 큐 생성
    response_queue = q.Queue()

    # 비동기 실행
    request_respond = threading.Thread(
        target=responseOpenAI,
        args=(kakaorequest, response_queue, filename)
    )
    request_respond.start()

    # 4.5초 타이머
    while(time.time() - start_time < 4.5):
        if not response_queue.empty():
            response = response_queue.get()
            run_flag = True
            break
        time.sleep(0.01)

    # 타임오버
    if run_flag == False:
        response = timeover()

    return {
        'statusCode': 200,
        'body': json.dumps(response),
        'headers': {'Access-Control-Allow-Origin': '*'}
    }

