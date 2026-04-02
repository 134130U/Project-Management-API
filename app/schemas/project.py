from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

from app.schemas.file import FileResponse

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "active"
    priority: Optional[str] = "Medium"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[int] = 0
    spent: Optional[int] = 0
    team: Optional[str] = None
    stakeholders: Optional[str] = None
    tags: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[int] = None
    spent: Optional[int] = None
    team: Optional[str] = None
    stakeholders: Optional[str] = None
    tags: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    files: Optional[list[FileResponse]] = []

    class Config:
        orm_mode = True
