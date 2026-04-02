from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.models.file import File as FileModel
from app.models.update import Update
from app.services.storage.factory import get_storage
from app.api.deps import get_current_user, get_db
from app.core.exceptions import NotFoundException

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)

storage = get_storage()

@router.post("/upload/{update_id}")
def upload_file(
    update_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    update = db.query(Update).filter(
        Update.id == update_id
    ).first()

    if not update:
        raise NotFoundException(resource="Update")

    # Read file data to get its size
    file_data = file.file.read()
    size = len(file_data)
    
    # Upload from the byte data
    key = storage.upload(file_data)

    db_file = FileModel(
        project_id=update.project_id,
        update_id=update_id,
        storage_key=key,
        filename=file.filename,
        size=size,
        mime_type=file.content_type
    )

    db.add(db_file)
    db.commit()

    return {
        "message": "uploaded",
        "key": key
    }

@router.get("/download/{file_id}")
def get_file_url(
    file_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    file = db.query(FileModel).filter(
        FileModel.id == file_id
    ).first()

    if not file:
        raise NotFoundException(resource="File")

    url = storage.get_url(
        file.storage_key
    )

    return {
        "url": url
    }

@router.get("/update/{update_id}")
def list_files(
    update_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    files = db.query(FileModel).filter(
        FileModel.update_id == update_id
    ).all()

    return files