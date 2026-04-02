from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    update_id = Column(Integer, ForeignKey("updates.id"), nullable=True)
    storage_key = Column(String)
    filename = Column(String)
    size = Column(Integer)
    mime_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="files")
    update = relationship("Update", back_populates="files")
