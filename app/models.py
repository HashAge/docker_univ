from sqlalchemy import Column, String
from database import Base

class Item(Base):
    __tablename__ = "items"
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)

