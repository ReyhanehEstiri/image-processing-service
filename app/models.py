from sqlalchemy import Column, Integer, String
from .database import Base

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    format = Column(String)
    width = Column(Integer)
    height = Column(Integer)
    size_bytes = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
