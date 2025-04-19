import os
import io
import csv
import uuid
import time
from minio import Minio
from minio.error import S3Error
from sqlalchemy import text
from database import SessionLocal
from datetime import timedelta

BUCKET_NAME = "reports"

# Надёжное подключение к MinIO с повторными попытками
for attempt in range(10):
    try:
        minio_client = Minio(
            endpoint=os.getenv("MINIO_URL", "minio:9000").replace("http://", ""),
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            secure=False,
        )

        if not minio_client.bucket_exists(BUCKET_NAME):
            minio_client.make_bucket(BUCKET_NAME)
        break  # Успешно подключились и создали бакет/он уже есть

    except S3Error as e:
        print(f"[{attempt+1}/10] MinIO not ready yet: {e}")
        time.sleep(2)

else:
    raise Exception("❌ Не удалось подключиться к MinIO после 10 попыток")

# Функция генерации и загрузки отчёта
def generate_and_upload_csv_report():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT * FROM items"))
        rows = result.mappings().all()
        

        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=["id", "name", "description"])
        writer.writeheader()
        writer.writerows(rows)

        file_bytes = io.BytesIO(buffer.getvalue().encode("utf-8"))
        filename = f"{uuid.uuid4()}.csv"

        minio_client.put_object(
            bucket_name=BUCKET_NAME,
            object_name=filename,
            data=file_bytes,
            length=file_bytes.getbuffer().nbytes,
            content_type="text/csv"
        )

        url = minio_client.presigned_get_object(
            bucket_name=BUCKET_NAME,
            object_name=filename,
            expires=timedelta(seconds=3600)
        )
        return url
    finally:
        db.close()
