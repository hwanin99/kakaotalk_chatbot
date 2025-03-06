import os
import time
import json
import threading
import queue as q

from utils.get_response import getTextFromGPT,getImageURLFromDALLE,textResponseFormat,imageResponseFormat
from utils.asynchronous import timeover


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
