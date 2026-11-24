from fastapi import APIRouter, Depends, Response

from app.db.database import get_db
from app.dependencies import get_current_user
from app.schemas.schemas import MemberAdd, ProjectCreate, ProjectUpdate
from app.services import project_service, task_service

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.get("")
def list_projects(db=Depends(get_db), user=Depends(get_current_user)):
    return project_service.list_projects(db, user)


@router.post("", status_code=201)
def create_project(data: ProjectCreate, db=Depends(get_db), user=Depends(get_current_user)):
    return project_service.create_project(db, user, data)


@router.patch("/{project_id}")
def update_project(
    project_id: int, data: ProjectUpdate, db=Depends(get_db), user=Depends(get_current_user)
):
    return project_service.update_project(db, user, project_id, data)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    project_service.delete_project(db, user, project_id)
    return Response(status_code=204)


@router.get("/{project_id}/members")
def list_members(project_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    return project_service.list_members(db, user, project_id)


@router.post("/{project_id}/members", status_code=201)
def add_member(
    project_id: int, data: MemberAdd, db=Depends(get_db), user=Depends(get_current_user)
):
    return project_service.add_member(db, user, project_id, data)


@router.delete("/{project_id}/members/{user_id}", status_code=204)
def remove_member(
    project_id: int, user_id: int, db=Depends(get_db), user=Depends(get_current_user)
):
    project_service.remove_member(db, user, project_id, user_id)
    return Response(status_code=204)


@router.get("/{project_id}/tasks")
def list_project_tasks(project_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    return task_service.list_tasks(db, user, project_id)
