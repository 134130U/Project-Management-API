from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FileBase(BaseModel):
    filename: str
    storage_key: str
    mime_type: str
    size: int

class FileCreate(FileBase):
    project_id: Optional[int] = None
    update_id: Optional[int] = None

class FileResponse(FileBase):
    id: int
    project_id: Optional[int] = None
    update_id: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True