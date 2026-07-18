import uuid

from utils.config import AWS_REGION, AWS_S3_BUCKET, s3


# =========================================================
# S3 업로드
# =========================================================
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
