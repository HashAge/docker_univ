from fastapi import FastAPI
from database import SessionLocal
from models import Item

app = FastAPI()

@app.get("/report")
def generate_report():
    db = SessionLocal()
    items = db.query(Item).all()
    db.close()
    return {"report": [item.name for item in items]}
