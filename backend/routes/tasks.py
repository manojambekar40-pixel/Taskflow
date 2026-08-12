"""
routes/tasks.py
----------------
Task CRUD, the custom-algorithm sort endpoint, the custom-algorithm
search endpoint, and the AI Quick Add endpoint.

IMPORTANT ORDERING: FastAPI matches routes top-to-bottom. The literal
paths /tasks/search and /tasks/quick-add are declared BEFORE the
dynamic /tasks/{task_id} route so they are never shadowed by it.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend import crud, schemas
from backend.dependencies import get_db
from backend.algorithms import insertion_sort, binary_search, linear_search
from backend.groq_service import parse_with_ai

router = APIRouter(prefix="/tasks", tags=["tasks"])

PRIORITY_WEIGHT = {"low": 1, "medium": 2, "high": 3}


def _task_to_dict(task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "priority": task.priority,
        "due_date": task.due_date,
        "project_id": task.project_id,
    }


# ---------------------------------------------------------------- Create --
@router.post("", response_model=schemas.TaskResponse, status_code=201)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    project = crud.get_project(db, task.project_id)
    if project is None:
        raise HTTPException(status_code=422, detail="project_id does not reference an existing project")
    return crud.create_task(db, task)


# ------------------------------------------------------------------ List --
@router.get("", response_model=list[schemas.TaskResponse])
def list_tasks(
    project_id: Optional[int] = Query(default=None),
    sort: Optional[str] = Query(default=None, description="Set to 'priority' to sort with custom insertion sort"),
    db: Session = Depends(get_db),
):
    tasks = crud.get_tasks(db, project_id=project_id)
    task_dicts = [_task_to_dict(t) for t in tasks]

    if sort == "priority":
        # Custom insertion_sort — NOT sorted()/list.sort() — as required.
        insertion_sort(task_dicts, key=lambda t: PRIORITY_WEIGHT[t["priority"]])

    return task_dicts


# ---------------------------------------------------------------- Search --
@router.get("/search")
def search_tasks(
    title: str = Query(..., description="Exact title to search for"),
    algo: str = Query(default="linear", pattern="^(binary|linear)$"),
    db: Session = Depends(get_db),
):
    tasks = crud.get_tasks(db)
    task_dicts = [_task_to_dict(t) for t in tasks]

    if algo == "binary":
        # Binary search requires a sorted index; build + sort it with our
        # own insertion_sort, then search with our own binary_search.
        index = [{"id": t["id"], "title": t["title"]} for t in task_dicts]
        insertion_sort(index, key=lambda r: r["title"])
        found_index = binary_search(index, title, key=lambda r: r["title"])
    else:
        index = [{"id": t["id"], "title": t["title"]} for t in task_dicts]
        found_index = linear_search(index, title, key=lambda r: r["title"])

    if found_index == -1:
        raise HTTPException(status_code=404, detail="Task not found")

    matched_id = index[found_index]["id"]
    matched_task = next(t for t in task_dicts if t["id"] == matched_id)
    return matched_task


# ------------------------------------------------------------- Quick Add --
@router.post("/quick-add", response_model=schemas.TaskResponse, status_code=201)
def quick_add_task(payload: schemas.QuickAddRequest, db: Session = Depends(get_db)):
    project = crud.get_project(db, payload.project_id)
    if project is None:
        raise HTTPException(status_code=422, detail="project_id does not reference an existing project")

    parsed = parse_with_ai(payload.description)

    task_create = schemas.TaskCreate(
        title=parsed.title,
        priority=parsed.priority,
        due_date=parsed.due_date_hint,
        project_id=payload.project_id,
    )
    return crud.create_task(db, task_create)


# ------------------------------------------------------------ Get by id --
@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# --------------------------------------------------------------- Update --
@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    if task_update.project_id is not None:
        project = crud.get_project(db, task_update.project_id)
        if project is None:
            raise HTTPException(status_code=422, detail="project_id does not reference an existing project")

    updated = crud.update_task(db, task_id, task_update)
    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


# --------------------------------------------------------------- Delete --
@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    success = crud.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}
