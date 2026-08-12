"""
schemas.py
----------
Pydantic v2 request/response schemas for TaskFlow.
"""

from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator

Priority = Literal["low", "medium", "high"]


# ---------------------------------------------------------------- Users ---
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name cannot be empty or whitespace")
        return v.strip()


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = {"from_attributes": True}


# ------------------------------------------------------------- Projects ---
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    owner_id: int

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name cannot be empty or whitespace")
        return v.strip()


class ProjectResponse(BaseModel):
    id: int
    name: str
    owner_id: int

    model_config = {"from_attributes": True}


class ProjectStatistics(BaseModel):
    project_id: int
    project_name: str
    task_count: int
    low_count: int
    medium_count: int
    high_count: int


# ---------------------------------------------------------------- Tasks ---
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    priority: Priority
    due_date: Optional[str] = Field(default=None, max_length=50)
    project_id: int

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("title cannot be empty or whitespace")
        return stripped


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    priority: Optional[Priority] = None
    due_date: Optional[str] = Field(default=None, max_length=50)
    project_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        stripped = v.strip()
        if not stripped:
            raise ValueError("title cannot be empty or whitespace")
        return stripped


class TaskResponse(BaseModel):
    id: int
    title: str
    priority: Priority
    due_date: Optional[str]
    project_id: int

    model_config = {"from_attributes": True}


# ------------------------------------------------------------- Quick Add --
class QuickAddRequest(BaseModel):
    description: str = Field(..., min_length=1)
    project_id: int

    @field_validator("description")
    @classmethod
    def description_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("description cannot be empty or whitespace")
        return v


class ParsedTask(BaseModel):
    """Validated shape of parser output (mock or Groq) before DB insert."""
    title: str = Field(..., min_length=1)
    priority: Priority
    due_date_hint: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("title cannot be empty")
        return stripped
