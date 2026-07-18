import base64

from utils.config import client
from utils.s3_utils import upload_to_s3
from utils.state import write_state


# =========================================================
# 이미지 설명 (캡션 생성)
# =========================================================
def chatgpt(image_url):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "다음 이미지를 설명해 주세요."},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }],
    )
    return response.choices[0].message.content


def build_prompt(image_url, style):
    """캡션(구조 설명)과 사용자 스타일을 결합해 최종 프롬프트 구성."""
    caption = chatgpt(image_url)
    return (
        f"다음은 원본 평면도 이미지에 대한 상세 설명이다:\n\n"
        f"{caption}\n\n"
        f"위 설명을 기반으로, 원본 이미지와 동일한 구조, 동일한 비율, 동일한 공간 배치, 동일한 벽과 문 위치를 유지하면서 이미지의 가장자리(특히 좌우)가 잘리면 안 되며,"
        f"건축적 형태는 절대 변경하지 말고, 내부 인테리어 스타일만 '{style}' 스타일로 재구성한 2D 이미지를 원본과 동일한 캔버스 크기와 비율로 생성해줘.\n\n"
        f"- 이미지 크기와 화각(viewpoint)은 원본과 동일하게 유지\n"
        f"- 글씨나 텍스트 요소, 배경색은 절대 넣지 말 것\n"
        f"- 방의 구조, 면적, 형태, 출입구 위치는 원본 그대로 유지\n"
        f"- 변경되는 요소는 색감, 마감재, 조명, 가구 배치 등 인테리어 요소만\n"
        f"- 결과는 실제 인테리어 렌더링처럼 자연스럽고 전문적으로 보이게\n"
    )


# =========================================================
# 이미지 생성 (워커에서 호출됨) — 결과/실패 상태를 S3에 기록
# =========================================================
def image_generate(image_url, ko_style, user_id):
    print(">>> image_generate START")

    style = ko_style

    prompt = build_prompt(image_url, style)

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
        tools=[{"type": "image_generation"}],
    )
    print(">>> responses.create 완료")

    image_generation_calls = [
        output for output in response.output if output.type == "image_generation_call"
    ]
    image_data = [output.result for output in image_generation_calls]

    if image_data:
        image_base64 = image_data[0]
        file_path = "/tmp/interior.png"
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(image_base64))

        print(">>> S3 업로드 시작")
        image_url_s3 = upload_to_s3(file_path)
        print(">>> S3 업로드 완료")

        # ✅ 완료 상태를 S3에 기록
        write_state(user_id, f"DONE,{image_url},{ko_style},{image_url_s3}")
        print(">>> image_generate END")
        return image_url_s3

    print("⚠️ 이미지 생성 실패:")
    print(response.output)
    # ❌ 실패 상태 기록 (무한 GENERATING 방지)
    write_state(user_id, f"ERROR,{image_url},{ko_style},")
    return None
