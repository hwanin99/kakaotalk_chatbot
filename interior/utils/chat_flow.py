import json
import os

from utils.config import lambda_client
from utils.kakao_format import (
    imageWithTextFormat,
    quickReplyFormat,
    textResponseFormat,
    timeover,
)
from utils.state import parse_state, read_state, reset_state, write_state


# =========================================================
# 대화 처리 로직 (상태는 S3에 user_id 별로 저장)
# =========================================================
def responseOpenAI(request, response_queue):
    user_id = request.get("userRequest", {}).get("user", {}).get("id", "anonymous")
    user_input = request["userRequest"]["utterance"].strip()

    # 1️⃣ 상담 시작 / 종료
    if "상담 시작" in user_input or "상담시작" in user_input:
        try:
            write_state(user_id, "START,,,")
        except Exception as e:
            print(f"write_state error(상담 시작): {e}")
            response_queue.put(textResponseFormat(
                "상태 저장에 실패했어요. 😢\n(S3 권한 설정을 확인해주세요.)"
            ))
            return
        response_queue.put(
            textResponseFormat("상담을 시작합니다!\n먼저 이미지 URL을 입력해주세요.")
        )
        return

    if "상담 종료" in user_input or "상담종료" in user_input:
        reset_state(user_id)
        response_queue.put(textResponseFormat("상담이 종료되었습니다.\n다음에 또 만나요! 🤗"))
        return

    # 현재 상태 읽기
    last_update = read_state(user_id)

    if not last_update:
        response_queue.put(textResponseFormat("반가워요. 🤗\n상담 시작을 먼저 입력해주세요!"))
        return

    parts = parse_state(last_update)

    # 2️⃣ URL 입력 단계
    if parts[0] == "START" and parts[1] == '' and parts[2] == '' and parts[3] == '':
        if user_input.startswith("http"):
            try:
                write_state(user_id, f"START,{user_input},,")
            except Exception as e:
                print(f"write_state error(URL 저장): {e}")
                response_queue.put(textResponseFormat(
                    "URL 저장에 실패했어요. 😢\n(S3 권한 설정을 확인해주세요.)"
                ))
                return
            response_queue.put(imageWithTextFormat(
                user_input,
                '원본 이미지',
                "이미지 URL을 저장했어요!\n이제 원하는 스타일을 입력해주세요."
            ))
            return

        response_queue.put(textResponseFormat("올바른 URL 형식인지 확인해주세요!"))
        return

    # 3️⃣ 스타일 입력 단계 (생성 X)
    if parts[0] == 'START' and parts[1] != '' and parts[2] == '' and parts[3] == '':
        image_url = parts[1]
        style = user_input
        try:
            write_state(user_id, f"START,{image_url},{style},")
        except Exception as e:
            print(f"write_state error(스타일 저장): {e}")
            response_queue.put(textResponseFormat(
                "스타일 저장에 실패했어요. 😢\n(S3 권한 설정을 확인해주세요.)"
            ))
            return
        response_queue.put(quickReplyFormat(
            f"'{style}' 스타일을 저장했어요!\n이제 이미지를 생성해 볼까요?",
            '이미지 생성하기'
        ))
        return

    # 4️⃣ 이미지 생성하기 → 워커 async 호출 후 즉시 응답
    if "이미지 생성하기" in user_input:
        if parts[0] != '' and parts[1] != '' and parts[2] != '':
            image_url = parts[1]
            style = parts[2]

            # 상태를 GENERATING 으로 표시
            try:
                write_state(user_id, f"GENERATING,{image_url},{style},")
            except Exception as e:
                print(f"write_state error(GENERATING): {e}")
                response_queue.put(textResponseFormat(
                    "상태 저장에 실패했어요. 😢\n(S3 권한 설정을 확인해주세요.)"
                ))
                return

            # 같은 Lambda 를 비동기로 self-invoke (freeze 영향 없이 끝까지 실행됨)
            try:
                lambda_client.invoke(
                    FunctionName=os.environ["AWS_LAMBDA_FUNCTION_NAME"],
                    InvocationType="Event",
                    Payload=json.dumps({
                        "worker": True,
                        "user_id": user_id,
                        "image_url": image_url,
                        "style": style,
                    }),
                )
            except Exception as e:
                print(f"lambda invoke error: {e}")
                write_state(user_id, f"ERROR,{image_url},{style},")
                response_queue.put(textResponseFormat(
                    "이미지 생성 요청에 실패했어요. 😢\n(lambda:InvokeFunction 권한을 확인해주세요.)"
                ))
                return

            # 즉시 "생성 중" 응답
            response_queue.put(timeover(
                "이미지를 생성하고 있어요! 🛠️\n20~40초 정도 걸려요.\n잠시 후 아래 '이미지 불러오기'를 눌러주세요."
            ))
            return

        response_queue.put(textResponseFormat("먼저 이미지 URL과 스타일을 입력해주세요!"))
        return

    # 5️⃣ 이미지 불러오기 → S3 상태 확인
    if "이미지 불러오기" in user_input:
        parts = parse_state(read_state(user_id))
        state = parts[0]

        if state == "DONE":
            style = parts[2]
            bot_res = parts[3]
            response_queue.put(imageWithTextFormat(
                bot_res,
                f"{style} 스타일의 인테리어 디자인",
                f"{style} 스타일로 변경된 디자인이에요!"
            ))
            reset_state(user_id)
            return

        if state == "GENERATING":
            response_queue.put(timeover(
                "아직 생성 중이에요! ⏳\n조금만 더 기다렸다가 다시 '이미지 불러오기'를 눌러주세요."
            ))
            return

        if state == "ERROR":
            response_queue.put(textResponseFormat(
                "이미지 생성에 실패했어요. 😢\n'이미지 생성하기'로 다시 시도해주세요."
            ))
            return

        response_queue.put(textResponseFormat("먼저 '이미지 생성하기'를 진행해주세요!"))
        return

    # 그 외 입력
    response_queue.put(textResponseFormat(
        "안내에 따라 진행해주세요!\n(상담 시작 → URL → 스타일 → 이미지 생성하기)"
    ))
    return
