from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from uuid import uuid4
from models import Item
from schemas import ItemCreate, ItemUpdate
from database import SessionLocal, engine
from sqlalchemy.orm import Session
import httpx

Item.metadata.create_all(bind=engine)
app = FastAPI()

@app.get("/")
def read_items():
    db = SessionLocal()
    items = db.query(Item).all()
    db.close()
    return items

@app.get("/{item_id}")
def read_item(item_id: str):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    db.close()
    if item:
        return item
    return JSONResponse(status_code=404, content={"detail": "Not found"})

@app.post("/")
def create_item(item: ItemCreate):
    db = SessionLocal()
    db_item = Item(id=str(uuid4()), name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

@app.put("/{item_id}")
def update_item(item_id: str, item: ItemUpdate):
    db = SessionLocal()
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        db.close()
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    db_item.name = item.name
    db_item.description = item.description
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

@app.delete("/{item_id}")
def delete_item(item_id: str):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        db.close()
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    db.delete(item)
    db.commit()
    db.close()
    return {"detail": "Deleted"}

@app.api_route("/reports/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_reports(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        url = f"http://report_service:8001/{path}"
        proxied_request = client.build_request(
            request.method,
            url,
            headers=request.headers.raw,
            content=await request.body()
        )
        response = await client.send(proxied_request)
        return JSONResponse(status_code=response.status_code, content=response.json())

