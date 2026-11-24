from datetime import date
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, EmailStr, StringConstraints

Status = Literal["TODO", "IN_PROGRESS", "DONE"]
Priority = Literal["LOW", "MEDIUM", "HIGH"]

FullName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Password = Annotated[str, StringConstraints(min_length=8, max_length=64)]
ProjectName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
TaskTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
CommentText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


# ---------- Auth ----------
class RegisterIn(BaseModel):
    full_name: FullName
    email: EmailStr
    password: Password


class LoginIn(BaseModel):
    email: str
    password: str


# ---------- Projects ----------
class ProjectCreate(BaseModel):
    name: ProjectName
    description: Optional[str] = None
    deadline: Optional[date] = None


class ProjectUpdate(BaseModel):
    name: Optional[ProjectName] = None
    description: Optional[str] = None
    deadline: Optional[date] = None


class MemberAdd(BaseModel):
    email: EmailStr


# ---------- Tasks ----------
class TaskCreate(BaseModel):
    project_id: int
    title: TaskTitle
    description: Optional[str] = None
    priority: Priority = "MEDIUM"
    deadline: Optional[date] = None
    assigned_to: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[TaskTitle] = None
    description: Optional[str] = None
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    deadline: Optional[date] = None
    assigned_to: Optional[int] = None


# ---------- Comments ----------
class CommentCreate(BaseModel):
    content: CommentText
