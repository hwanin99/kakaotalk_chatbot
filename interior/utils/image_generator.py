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

client = OpenAI(api_key="Change to your OpenAI API Key")

def chatgpt(image_url):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "다음 이미지를 설명해 주세요."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                    },
                },
            ],
        }],
    )
    return response.choices[0].message.content

# 🔑 환경 변수로 관리하는 게 좋음
AWS_S3_BUCKET = "Change to your AWS S3 BUCKET Name"
AWS_REGION = "Change to your AWS REGION"  # 서울 리전

# ✅ S3 클라이언트 생성
s3 = boto3.client(
    "s3",
    aws_access_key_id='Change to Your Key',
    aws_secret_access_key='Your Key',
    region_name=AWS_REGION
)

def upload_to_s3(file_path, bucket_name=AWS_S3_BUCKET):
    """로컬 파일을 S3에 업로드하고 공개 URL 반환"""
    file_name = f"{uuid.uuid4()}.png"
    s3.upload_file(
        Filename=file_path,
        Bucket=bucket_name,
        Key=file_name,
        ExtraArgs={"ContentType": "image/png"},
    )
    return f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{file_name}"

def image_generate(image_url, ko_style, filename):
    translator = Translator(from_lang='ko',to_lang='en')
    style = translator.translate(ko_style)

    prompt = (
        f"다음은 원본 평면도 이미지에 대한 상세 설명이다:\n\n"
        f"{chatgpt(image_url)}\n\n"
        f"위 설명을 기반으로, 원본 이미지와 동일한 구조, 동일한 비율, 동일한 공간 배치, 동일한 벽과 문 위치를 유지하면서 이미지의 가장자리(특히 좌우)가 잘리면 안 되며,"
        f"건축적 형태는 절대 변경하지 말고, 내부 인테리어 스타일만 '{style}' 스타일로 재구성한 2D 이미지를 원본과 동일한 캔버스 크기와 비율로 생성해줘.\n\n"
        f"- 이미지 크기와 화각(viewpoint)은 원본과 동일하게 유지\n"
        f"- 글씨나 텍스트 요소, 배경색은 절대 넣지 말 것\n"
        f"- 방의 구조, 면적, 형태, 출입구 위치는 원본 그대로 유지\n"
        f"- 변경되는 요소는 색감, 마감재, 조명, 가구 배치 등 인테리어 요소만\n"
        f"- 결과는 실제 인테리어 렌더링처럼 자연스럽고 전문적으로 보이게\n"
    )   # You can change the prompt to whatever you want.

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": image_url},
                ],
            }
        ],
        tools=[{"type": "image_generation", "input_fidelity": "high"}],
    )

    image_generation_calls = [
        output for output in response.output if output.type == "image_generation_call"
    ]
    image_data = [output.result for output in image_generation_calls]

    if image_data:
        image_base64 = image_data[0]
        file_path = "/tmp/interior.png"  # Change to your output image name

        with open(file_path, "wb") as f:
            f.write(base64.b64decode(image_base64))

        # ✅ S3 업로드
        image_url_s3 = upload_to_s3(file_path)
        with open(filename, "w") as f:
            f.write(f"DONE,{image_url},{ko_style},{image_url_s3}")

        return image_url_s3

    else:
        print("⚠️ 이미지 생성 실패:")
        print(response.output.content)
        return None

