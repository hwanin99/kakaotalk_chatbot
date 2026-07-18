import json
import queue as q
import threading
import time

from utils.chat_flow import responseOpenAI
from utils.kakao_format import timeover
from utils.openai_utils import image_generate
from utils.state import write_state


# =========================================================
# 메인 핸들러 — worker 경로 / 카카오 경로 분기
# =========================================================
def lambda_handler(event, context):
    # ---------- 워커(비동기) 경로 ----------
    # image_generate 를 freeze 영향 없는 별도 인보케이션에서 끝까지 실행
    if isinstance(event, dict) and event.get("worker"):
        user_id = event["user_id"]
        try:
            image_generate(event["image_url"], event["style"], user_id)
        except Exception as e:
            print(f"worker error: {e}")
            try:
                write_state(user_id, f"ERROR,{event['image_url']},{event['style']},")
            except Exception as e2:
                print(f"worker write_state(ERROR) 실패: {e2}")
        return {"statusCode": 200}

    # ---------- 카카오 경로 ----------
    run_flag = False
    start_time = time.time()

    kakaorequest = json.loads(event['body'])

    response_queue = q.Queue()
    request_respond = threading.Thread(
        target=responseOpenAI,
        args=(kakaorequest, response_queue)
    )
    request_respond.start()

    # 4.5초 타이머 (카카오 5초 제약 대비)
    while (time.time() - start_time < 4.5):
        if not response_queue.empty():
            response = response_queue.get()
            run_flag = True
            break
        time.sleep(0.01)

    if run_flag is False:
        response = timeover()

    return {
        'statusCode': 200,
        'body': json.dumps(response),
        'headers': {'Access-Control-Allow-Origin': '*'}
    }
