from app.db.database import execute, fetch_all, fetch_one
from app.errors import AppError
from app.services.common import (
    build_update,
    get_membership,
    get_project_or_404,
    require_member,
    require_owner,
)


def _project_view(db, project_id, user_id):
    return fetch_one(
        db,
        """SELECT p.id, p.name, p.description, p.deadline, p.owner_id, p.created_at,
                  pm.member_role AS my_role
           FROM projects p
           JOIN project_members pm ON pm.project_id = p.id AND pm.user_id = %s
           WHERE p.id = %s""",
        (user_id, project_id),
    )


def list_projects(db, user):
    return fetch_all(
        db,
        """SELECT p.id, p.name, p.description, p.deadline, p.owner_id, p.created_at,
                  pm.member_role AS my_role
           FROM projects p
           JOIN project_members pm ON pm.project_id = p.id
           WHERE pm.user_id = %s
           ORDER BY p.created_at DESC, p.id DESC""",
        (user["id"],),
    )


def create_project(db, user, data):
    # Projekti dhe anëtarësimi i Owner-it ruhen së bashku (transaksion)
    try:
        project_id = execute(
            db,
            "INSERT INTO projects (owner_id, name, description, deadline) VALUES (%s, %s, %s, %s)",
            (user["id"], data.name, data.description, data.deadline),
            commit=False,
        )
        execute(
            db,
            "INSERT INTO project_members (project_id, user_id, member_role) VALUES (%s, %s, 'OWNER')",
            (project_id, user["id"]),
            commit=False,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return _project_view(db, project_id, user["id"])


def update_project(db, user, project_id, data):
    get_project_or_404(db, project_id)
    require_owner(db, project_id, user["id"])
    fields = build_update(data, not_nullable=("name",))

    sets = ", ".join(f"{column} = %s" for column in fields)
    execute(db, f"UPDATE projects SET {sets} WHERE id = %s", (*fields.values(), project_id))
    return _project_view(db, project_id, user["id"])


def delete_project(db, user, project_id):
    get_project_or_404(db, project_id)
    require_owner(db, project_id, user["id"])
    execute(db, "DELETE FROM projects WHERE id = %s", (project_id,))


def list_members(db, user, project_id):
    get_project_or_404(db, project_id)
    require_member(db, project_id, user["id"])
    return fetch_all(
        db,
        """SELECT u.id AS user_id, u.full_name, u.email, pm.member_role
           FROM project_members pm
           JOIN users u ON u.id = pm.user_id
           WHERE pm.project_id = %s
           ORDER BY pm.member_role DESC, u.full_name""",
        (project_id,),
    )


def add_member(db, user, project_id, data):
    get_project_or_404(db, project_id)
    require_owner(db, project_id, user["id"])

    email = data.email.lower()
    target = fetch_one(db, "SELECT id, full_name, email FROM users WHERE email = %s", (email,))
    if target is None:
        raise AppError(404, "USER_NOT_FOUND", "No user is registered with this email.")
    if get_membership(db, project_id, target["id"]) is not None:
        raise AppError(409, "ALREADY_MEMBER", "This user is already a member of the project.")

    execute(
        db,
        "INSERT INTO project_members (project_id, user_id, member_role) VALUES (%s, %s, 'MEMBER')",
        (project_id, target["id"]),
    )
    return {
        "user_id": target["id"],
        "full_name": target["full_name"],
        "email": target["email"],
        "member_role": "MEMBER",
    }


def remove_member(db, user, project_id, member_id):
    get_project_or_404(db, project_id)
    require_owner(db, project_id, user["id"])

    target = get_membership(db, project_id, member_id)
    if target is None:
        raise AppError(404, "MEMBER_NOT_FOUND", "This user is not a member of the project.")
    if target["member_role"] == "OWNER":
        raise AppError(400, "CANNOT_REMOVE_OWNER", "The project owner cannot be removed.")

    try:
        # Detyrat e anëtarit të hequr bëhen të pacaktuara
        execute(
            db,
            "UPDATE tasks SET assigned_to = NULL WHERE project_id = %s AND assigned_to = %s",
            (project_id, member_id),
            commit=False,
        )
        execute(
            db,
            "DELETE FROM project_members WHERE project_id = %s AND user_id = %s",
            (project_id, member_id),
            commit=False,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
