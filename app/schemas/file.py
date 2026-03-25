from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FileBase(BaseModel):
    filename: str
    storage_key: str
    mime_type: str
    size: int

class FileCreate(FileBase):
    update_id: int

class FileResponse(FileBase):
    id: int
    update_id: int
    created_at: datetime

    class Config:
        from_attributes = True