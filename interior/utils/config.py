import os

import boto3
from openai import OpenAI

# =========================================================
# 설정 (하드코딩 금지: 키는 환경변수 / IAM Role 로 관리)
# =========================================================
AWS_S3_BUCKET = "hwanin99"
AWS_REGION = "ap-northeast-2"

# 상태 저장용 S3 접두어 (/tmp 대신 사용)
STATE_PREFIX = "state/"

# OpenAI 키는 반드시 Lambda 환경변수(OPENAI_API_KEY)로 주입
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# S3 / Lambda 클라이언트: 액세스 키 하드코딩 대신 실행 역할(Role) 자격증명 사용
#  ⚠️ 실행 역할(kakao_chatbot-role-...)에 아래 권한 필요:
#     - s3:GetObject, s3:PutObject  -> arn:aws:s3:::hwanin99/*
#     - s3:ListBucket               -> arn:aws:s3:::hwanin99   (NoSuchKey 정상 처리용)
#     - lambda:InvokeFunction       -> *                       (self-invoke용)
s3 = boto3.client("s3", region_name=AWS_REGION)
lambda_client = boto3.client("lambda", region_name=AWS_REGION)
