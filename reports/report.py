from database import SessionLocal
from sqlalchemy import text

def generate_report():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT * FROM items"))
        rows = result.fetchall()
        return [dict(row) for row in rows]
    finally:
        db.close()
