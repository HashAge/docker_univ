from sqlalchemy import Table, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

Item = Table(
    "items",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("name", String),
    Column("description", String),
)
