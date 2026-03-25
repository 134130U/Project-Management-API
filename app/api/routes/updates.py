from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.update import Update
from app.schemas.update import UpdateCreate, UpdateResponse
from app.api.deps import get_current_user, get_db
from app.models.project import Project
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/updates", tags=["Updates"])

@router.post("", response_model=UpdateResponse)
def create_update(
    update_in: UpdateCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == update_in.project_id,
        Project.owner_id == user.id
    ).first()
    if not project:
        raise NotFoundException(resource="Project")
        
    update = Update(**update_in.dict())
    db.add(update)
    db.commit()
    db.refresh(update)
    return update

@router.get("/{project_id}", response_model=list[UpdateResponse])
def list_updates(
    project_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id
    ).first()
    if not project:
        raise NotFoundException(resource="Project")
        
    return db.query(Update).filter(Update.project_id == project_id).all()