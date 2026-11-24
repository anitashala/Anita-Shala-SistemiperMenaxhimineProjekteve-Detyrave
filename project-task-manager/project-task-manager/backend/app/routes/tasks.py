from fastapi import APIRouter, Depends, Response

from app.db.database import get_db
from app.dependencies import get_current_user
from app.schemas.schemas import TaskCreate, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.post("", status_code=201)
def create_task(data: TaskCreate, db=Depends(get_db), user=Depends(get_current_user)):
    return task_service.create_task(db, user, data)


@router.patch("/{task_id}")
def update_task(
    task_id: int, data: TaskUpdate, db=Depends(get_db), user=Depends(get_current_user)
):
    return task_service.update_task(db, user, task_id, data)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    task_service.delete_task(db, user, task_id)
    return Response(status_code=204)
