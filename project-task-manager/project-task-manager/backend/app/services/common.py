from app.db.database import fetch_one
from app.errors import AppError


def get_project_or_404(db, project_id):
    project = fetch_one(db, "SELECT * FROM projects WHERE id = %s", (project_id,))
    if project is None:
        raise AppError(404, "PROJECT_NOT_FOUND", "Project does not exist.")
    return project


def get_membership(db, project_id, user_id):
    return fetch_one(
        db,
        "SELECT member_role FROM project_members WHERE project_id = %s AND user_id = %s",
        (project_id, user_id),
    )


def require_member(db, project_id, user_id):
    membership = get_membership(db, project_id, user_id)
    if membership is None:
        raise AppError(403, "FORBIDDEN", "You are not a member of this project.")
    return membership


def require_owner(db, project_id, user_id):
    membership = require_member(db, project_id, user_id)
    if membership["member_role"] != "OWNER":
        raise AppError(403, "FORBIDDEN", "Only the project owner can do this.")
    return membership


def build_update(data, not_nullable=()):
    """Merr vetëm fushat e dërguara nga klienti (PATCH). Emrat e kolonave vijnë nga schema, jo nga përdoruesi."""
    fields = data.model_dump(exclude_unset=True)
    for name in not_nullable:
        if name in fields and fields[name] is None:
            raise AppError(400, "VALIDATION_ERROR", f"{name} cannot be null.")
    if not fields:
        raise AppError(400, "VALIDATION_ERROR", "No fields to update.")
    return fields
