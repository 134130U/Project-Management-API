from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.db.base import Base
from datetime import datetime

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    update_id = Column(Integer, ForeignKey("updates.id"))
    storage_key = Column(String)
    filename = Column(String)
    size = Column(Integer)
    mime_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
