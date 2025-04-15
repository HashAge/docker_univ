from fastapi import FastAPI, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from models import Item
from schemas import ItemCreate, ItemUpdate, ItemOut
import uuid
import httpx
from minio import Minio

app = FastAPI()
init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/items", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()

@app.get("/items/{item_id}", response_model=ItemOut)
def get_item(item_id: uuid.UUID, db: Session = Depends(get_db)):
    item = db.query(Item).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items", response_model=ItemOut)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/items/{item_id}", response_model=ItemOut)
def update_item(item_id: uuid.UUID, updated: ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(Item).get(item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.name = updated.name
    db_item.description = updated.description
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: uuid.UUID, db: Session = Depends(get_db)):
    db_item = db.query(Item).get(item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"detail": "Deleted"}

@app.get("/report/download")
def get_report():
    response = httpx.post("http://report_service:8001/report")
    file_name = response.json()["file"]

    client = Minio("minio:9000",
                   access_key="minioadmin",
                   secret_key="minioadmin",
                   secure=False)

    data = client.get_object("reports", file_name)
    content = data.read()
    return Response(content=content, media_type="text/csv")
