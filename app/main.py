import os
import sys
import uuid
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

# Добавляем путь к папке app в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Теперь можно использовать абсолютные импорты
from app.database import SessionLocal, engine, Base
from app.models import Item
from app.schemas import ItemBase, ItemCreate, Item as ItemSchema

app = FastAPI()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Инициализация БД при старте
@app.on_event("startup")
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise

# Dependency для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_model=list[ItemSchema])
def read_items(db: Session = Depends(get_db)):
    """Получить все записи"""
    return db.query(Item).all()

@app.get("/{item_id}", response_model=ItemSchema)
def read_item(item_id: uuid.UUID, db: Session = Depends(get_db)):
    """Получить запись по ID"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/", response_model=ItemSchema)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Создать новую запись"""
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/{item_id}", response_model=ItemSchema)
def update_item(item_id: uuid.UUID, item: ItemCreate, db: Session = Depends(get_db)):
    """Обновить существующую запись"""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/{item_id}")
def delete_item(item_id: uuid.UUID, db: Session = Depends(get_db)):
    """Удалить запись"""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}
