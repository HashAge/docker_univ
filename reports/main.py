from fastapi import FastAPI
from report import generate_report

app = FastAPI()

@app.get("/report")
def get_report():
    return generate_report()
