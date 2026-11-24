from app.db.database import execute, fetch_all, fetch_one
from app.errors import AppError
from app.services.common import require_member


def _get_task_or_404(db, task_id):
    task = fetch_one(db, "SELECT id, project_id FROM tasks WHERE id = %s", (task_id,))
    if task is None:
        raise AppError(404, "TASK_NOT_FOUND", "Task does not exist.")
    return task


def list_comments(db, user, task_id):
    task = _get_task_or_404(db, task_id)
    require_member(db, task["project_id"], user["id"])
    return fetch_all(
        db,
        """SELECT c.id, c.task_id, c.author_id, u.full_name AS author_name, c.content, c.created_at
           FROM comments c
           JOIN users u ON u.id = c.author_id
           WHERE c.task_id = %s
           ORDER BY c.created_at, c.id""",
        (task_id,),
    )


def add_comment(db, user, task_id, data):
    task = _get_task_or_404(db, task_id)
    require_member(db, task["project_id"], user["id"])
    comment_id = execute(
        db,
        "INSERT INTO comments (task_id, author_id, content) VALUES (%s, %s, %s)",
        (task_id, user["id"], data.content),
    )
    return fetch_one(
        db,
        """SELECT c.id, c.task_id, c.author_id, u.full_name AS author_name, c.content, c.created_at
           FROM comments c JOIN users u ON u.id = c.author_id
           WHERE c.id = %s""",
        (comment_id,),
    )
