from fastapi import FastAPI
from report import generate_csv_report

app = FastAPI()

@app.post("/report")
def build_report():
    filename = generate_csv_report()
    return {"file": filename}
