from fastapi import APIRouter, Depends

from app.db.database import get_db
from app.dependencies import get_current_user
from app.schemas.schemas import CommentCreate
from app.services import comment_service

router = APIRouter(prefix="/api/tasks", tags=["Comments"])


@router.get("/{task_id}/comments")
def list_comments(task_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    return comment_service.list_comments(db, user, task_id)


@router.post("/{task_id}/comments", status_code=201)
def add_comment(
    task_id: int, data: CommentCreate, db=Depends(get_db), user=Depends(get_current_user)
):
    return comment_service.add_comment(db, user, task_id, data)
