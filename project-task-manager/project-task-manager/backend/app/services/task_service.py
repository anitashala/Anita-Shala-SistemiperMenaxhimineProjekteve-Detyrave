from app.db.database import execute, fetch_all, fetch_one
from app.errors import AppError
from app.services.common import (
    build_update,
    get_membership,
    get_project_or_404,
    require_member,
)

TASK_SELECT = """
    SELECT t.id, t.project_id, t.title, t.description, t.status, t.priority, t.deadline,
           t.assigned_to, u.full_name AS assigned_to_name,
           t.created_by, t.created_at, t.updated_at
    FROM tasks t
    LEFT JOIN users u ON u.id = t.assigned_to
"""


def _can_modify(task, role, user_id):
    """Vetëm Owner-i ose përgjegjësi i detyrës mund ta ndryshojë ose fshijë detyrën."""
    return role == "OWNER" or task["assigned_to"] == user_id


def _task_view(db, task_id, user_id):
    task = fetch_one(db, TASK_SELECT + " WHERE t.id = %s", (task_id,))
    membership = get_membership(db, task["project_id"], user_id)
    task["can_edit"] = bool(membership) and _can_modify(task, membership["member_role"], user_id)
    return task


def _get_task_or_404(db, task_id):
    task = fetch_one(db, "SELECT * FROM tasks WHERE id = %s", (task_id,))
    if task is None:
        raise AppError(404, "TASK_NOT_FOUND", "Task does not exist.")
    return task


def _check_assignee(db, project_id, assignee_id):
    if get_membership(db, project_id, assignee_id) is None:
        raise AppError(
            400, "ASSIGNEE_NOT_MEMBER", "The assigned user is not a member of this project."
        )


def _require_modify_permission(db, task, user_id):
    membership = require_member(db, task["project_id"], user_id)
    if not _can_modify(task, membership["member_role"], user_id):
        raise AppError(403, "FORBIDDEN", "You are not allowed to modify this task.")


def list_tasks(db, user, project_id):
    get_project_or_404(db, project_id)
    membership = require_member(db, project_id, user["id"])
    tasks = fetch_all(db, TASK_SELECT + " WHERE t.project_id = %s ORDER BY t.id", (project_id,))
    for task in tasks:
        task["can_edit"] = _can_modify(task, membership["member_role"], user["id"])
    return tasks


def create_task(db, user, data):
    get_project_or_404(db, data.project_id)
    require_member(db, data.project_id, user["id"])
    if data.assigned_to is not None:
        _check_assignee(db, data.project_id, data.assigned_to)

    task_id = execute(
        db,
        """INSERT INTO tasks (project_id, assigned_to, created_by, title, description, priority, deadline)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (
            data.project_id,
            data.assigned_to,
            user["id"],
            data.title,
            data.description,
            data.priority,
            data.deadline,
        ),
    )
    return _task_view(db, task_id, user["id"])


def update_task(db, user, task_id, data):
    task = _get_task_or_404(db, task_id)
    _require_modify_permission(db, task, user["id"])
    fields = build_update(data, not_nullable=("title", "status", "priority"))

    if fields.get("assigned_to") is not None:
        _check_assignee(db, task["project_id"], fields["assigned_to"])

    sets = ", ".join(f"{column} = %s" for column in fields)
    execute(db, f"UPDATE tasks SET {sets} WHERE id = %s", (*fields.values(), task_id))
    return _task_view(db, task_id, user["id"])


def delete_task(db, user, task_id):
    task = _get_task_or_404(db, task_id)
    _require_modify_permission(db, task, user["id"])
    execute(db, "DELETE FROM tasks WHERE id = %s", (task_id,))
