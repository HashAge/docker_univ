import csv
import io
import uuid
from minio import Minio

def generate_csv_report():
    data = [
        {"id": 1, "name": "Alpha"},
        {"id": 2, "name": "Beta"}
    ]

    filename = f"report_{uuid.uuid4().hex}.csv"
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["id", "name"])
    writer.writeheader()
    writer.writerows(data)

    # Сохраняем в MinIO
    client = Minio("minio:9000",
                   access_key="minioadmin",
                   secret_key="minioadmin",
                   secure=False)

    found = client.bucket_exists("reports")
    if not found:
        client.make_bucket("reports")

    client.put_object("reports", filename,
                      data=io.BytesIO(buffer.getvalue().encode("utf-8")),
                      length=len(buffer.getvalue()),
                      content_type="text/csv")

    return filename
