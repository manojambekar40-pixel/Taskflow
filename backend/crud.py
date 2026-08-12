"""
crud.py
-------
Database access functions, kept separate from route handlers so the
routing layer stays thin and the persistence logic is reusable/testable.
"""

from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend import models, schemas


# ---------------------------------------------------------------- Users ---
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session) -> List[models.User]:
    return db.query(models.User).all()


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


# ------------------------------------------------------------- Projects ---
def create_project(db: Session, project: schemas.ProjectCreate) -> models.Project:
    db_project = models.Project(name=project.name, owner_id=project.owner_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_projects(db: Session) -> List[models.Project]:
    return db.query(models.Project).all()


def get_project(db: Session, project_id: int) -> Optional[models.Project]:
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def get_project_statistics(db: Session) -> List[dict]:
    """
    Computed entirely in SQL using COUNT() + GROUP BY / CASE, never by
    pulling all tasks into Python and counting them there.
    """
    # SQLite/Postgres both support conditional aggregation via SUM(CASE...),
    # implemented with func.sum + case() for portability.
    from sqlalchemy import case

    rows = (
        db.query(
            models.Project.id.label("project_id"),
            models.Project.name.label("project_name"),
            func.count(models.Task.id).label("task_count"),
            func.sum(case((models.Task.priority == "low", 1), else_=0)).label("low_count"),
            func.sum(case((models.Task.priority == "medium", 1), else_=0)).label("medium_count"),
            func.sum(case((models.Task.priority == "high", 1), else_=0)).label("high_count"),
        )
        .outerjoin(models.Task, models.Task.project_id == models.Project.id)
        .group_by(models.Project.id, models.Project.name)
        .order_by(models.Project.id)
        .all()
    )

    return [
        {
            "project_id": row.project_id,
            "project_name": row.project_name,
            "task_count": row.task_count or 0,
            "low_count": row.low_count or 0,
            "medium_count": row.medium_count or 0,
            "high_count": row.high_count or 0,
        }
        for row in rows
    ]


# ---------------------------------------------------------------- Tasks ---
def create_task(db: Session, task: schemas.TaskCreate) -> models.Task:
    db_task = models.Task(
        title=task.title,
        priority=task.priority,
        due_date=task.due_date,
        project_id=task.project_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_tasks(db: Session, project_id: Optional[int] = None) -> List[models.Task]:
    query = db.query(models.Task)
    if project_id is not None:
        query = query.filter(models.Task.project_id == project_id)
    return query.all()


def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate) -> Optional[models.Task]:
    db_task = get_task(db, task_id)
    if db_task is None:
        return None
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    db_task = get_task(db, task_id)
    if db_task is None:
        return False
    db.delete(db_task)
    db.commit()
    return True
