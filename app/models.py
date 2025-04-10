import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, index=True)
    description = Column(String)
