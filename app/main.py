from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, init_db
from models import Base, Item
import httpx
import io
import uuid
from fastapi.responses import StreamingResponse

app = FastAPI()
init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/items")
def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()

@app.get("/items/{item_id}")
def read_item(item_id: str, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items")
def create_item(name: str, description: str, db: Session = Depends(get_db)):
    new_item = Item(id=str(uuid.uuid4()), name=name, description=description)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.put("/items/{item_id}")
def update_item(item_id: str, name: str, description: str, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.name = name
    item.description = description
    db.commit()
    db.refresh(item)
    return item

@app.delete("/items/{item_id}")
def delete_item(item_id: str, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"detail": "Item deleted"}

@app.get("/report/download")
async def download_report():
    async with httpx.AsyncClient() as client:
        # 1. Запросить ссылку у report_service
        try:
            response = await client.get("http://report_service:8001/report/download")
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при запросе отчёта: {str(e)}")

        url = data.get("url")
        if not url:
            raise HTTPException(status_code=500, detail="Не удалось получить ссылку на отчёт")

        # 2. Скачать файл по pre-signed URL
        file_response = await client.get(url)

        return StreamingResponse(io.BytesIO(file_response.content), media_type="text/csv", headers={
            "Content-Disposition": f"attachment; filename=report.csv"
        })
