from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="active")
    priority = Column(String, default="Medium")
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget = Column(Integer, default=0)
    spent = Column(Integer, default=0)
    team = Column(Text)
    stakeholders = Column(Text)
    tags = Column(Text)
    progress = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    files = relationship("File", back_populates="project", cascade="all, delete-orphan")
    updates = relationship("Update", back_populates="project", cascade="all, delete-orphan")