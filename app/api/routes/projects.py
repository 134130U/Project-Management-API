from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, Form
from sqlalchemy.orm import Session, joinedload
from app.models.project import Project
from app.models.file import File as FileModel
from app.schemas.project import ProjectResponse, ProjectUpdate
from app.models.update import Update
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.core.exceptions import NotFoundException
from app.services.storage.factory import get_storage
from typing import Optional
from datetime import datetime, date

router = APIRouter(prefix="/projects", tags=["Projects"])
storage = get_storage()

@router.post("", response_model=ProjectResponse)
def create_project(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    status: Optional[str] = Form("active"),
    priority: Optional[str] = Form("Medium"),
    start_date: Optional[date] = Form(None),
    end_date: Optional[date] = Form(None),
    budget: Optional[int] = Form(0),
    spent: Optional[int] = Form(0),
    team: Optional[str] = Form(None),
    stakeholders: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    progress: Optional[int] = Form(0),
    file: Optional[UploadFile] = FastAPIFile(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = Project(
        name=name,
        description=description,
        status=status,
        priority=priority,
        start_date=start_date,
        end_date=end_date,
        budget=budget,
        spent=spent,
        team=team,
        stakeholders=stakeholders,
        tags=tags,
        progress=progress,
        owner_id=current_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Re-fetch with files to be safe
    project = db.query(Project).options(joinedload(Project.files)).filter(Project.id == project.id).first()

    if file:
        file_data = file.file.read()
        key = storage.upload(file_data)
        db_file = FileModel(
            project_id=project.id,
            storage_key=key,
            filename=file.filename,
            size=0,
            mime_type=file.content_type
        )
        db.add(db_file)
        db.commit()
        db.refresh(project)

    return project

@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise NotFoundException(resource="Project")

    update_data = project_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return project

@router.get("", response_model=list[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Project).options(joinedload(Project.files)).filter(Project.owner_id == current_user.id).all()

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).options(joinedload(Project.files)).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise NotFoundException(resource="Project")
    return project

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise NotFoundException(resource="Project")

    # Delete all associated files from storage
    files = db.query(FileModel).filter(FileModel.project_id == project_id).all()
    for f in files:
        try:
            storage.delete(f.storage_key)
        except Exception as e:
            print(f"Error deleting file {f.storage_key}: {e}")

    # Delete project (cascading might handle DB, but let's be explicit if needed)
    # Actually, SQLAlchemy relationship with cascade="all, delete-orphan" would be better.
    # Let's check the models for cascade.
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}