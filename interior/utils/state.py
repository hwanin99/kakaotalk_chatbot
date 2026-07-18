from utils.config import AWS_S3_BUCKET, STATE_PREFIX, s3


# =========================================================
# S3 기반 상태 저장 헬퍼 (기존 CSV 포맷 "STATE,url,style,result" 유지)
# =========================================================
def _state_key(user_id):
    return f"{STATE_PREFIX}{user_id}.txt"


def read_state(user_id):
    """S3에서 상태 문자열 읽기. 상태가 아직 없으면 빈 문자열 반환.
    권한 오류 등 '진짜' 예외는 로그에 또렷이 남기고 빈 문자열 처리."""
    try:
        obj = s3.get_object(Bucket=AWS_S3_BUCKET, Key=_state_key(user_id))
        return obj["Body"].read().decode("utf-8").strip()
    except s3.exceptions.NoSuchKey:
        # 아직 상태 파일이 없는 정상 상황
        return ""
    except Exception as e:
        # AccessDenied 등은 여기로 들어옴 -> 로그로 원인 파악
        print(f"read_state error: {e}")
        return ""


def write_state(user_id, content):
    """S3에 상태 문자열 저장. 실패 시 예외를 그대로 전파(호출부에서 처리)."""
    s3.put_object(
        Bucket=AWS_S3_BUCKET,
        Key=_state_key(user_id),
        Body=content.encode("utf-8"),
        ContentType="text/plain",
    )


def reset_state(user_id):
    try:
        write_state(user_id, "")
    except Exception as e:
        print(f"reset_state error: {e}")


def parse_state(last_update):
    """상태 문자열을 4칸("STATE,url,style,result")으로 안전하게 분해."""
    parts = last_update.split(",")
    while len(parts) < 4:
        parts.append("")
    return parts
