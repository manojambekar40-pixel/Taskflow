"""routes/projects.py - Project CRUD + statistics endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import crud, schemas
from backend.dependencies import get_db

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=schemas.ProjectResponse, status_code=201)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    owner = crud.get_user(db, project.owner_id)
    if owner is None:
        raise HTTPException(status_code=422, detail="owner_id does not reference an existing user")
    return crud.create_project(db, project)


@router.get("", response_model=list[schemas.ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return crud.get_projects(db)


# NOTE: this concrete path is registered before any /{project_id}-style
# path elsewhere in the app to avoid path collisions.
@router.get("/statistics", response_model=list[schemas.ProjectStatistics])
def project_statistics(db: Session = Depends(get_db)):
    return crud.get_project_statistics(db)
