from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UpdateBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class UpdateCreate(UpdateBase):
    project_id: int

class UpdateUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class UpdateResponse(UpdateBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        orm_mode = True
