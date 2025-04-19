from fastapi import FastAPI
from report import generate_and_upload_csv_report

app = FastAPI()

@app.get("/report/download")
def download_report():
    url = generate_and_upload_csv_report()
    if url:
        return {"url": url}
    return {"url": None}
