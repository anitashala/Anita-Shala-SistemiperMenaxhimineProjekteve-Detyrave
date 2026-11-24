from app.db.database import fetch_all


def get_dashboard(db, user):
    user_id = user["id"]

    by_status = {"TODO": 0, "IN_PROGRESS": 0, "DONE": 0}
    rows = fetch_all(
        db,
        """SELECT t.status, COUNT(*) AS total
           FROM tasks t
           JOIN project_members pm ON pm.project_id = t.project_id
           WHERE pm.user_id = %s
           GROUP BY t.status""",
        (user_id,),
    )
    for row in rows:
        by_status[row["status"]] = row["total"]

    my_tasks = fetch_all(
        db,
        """SELECT t.id, t.project_id, t.title, t.status, t.deadline
           FROM tasks t
           WHERE t.assigned_to = %s
           ORDER BY t.deadline IS NULL, t.deadline, t.id""",
        (user_id,),
    )

    due_soon = fetch_all(
        db,
        """SELECT t.id, t.project_id, t.title, t.deadline
           FROM tasks t
           JOIN project_members pm ON pm.project_id = t.project_id
           WHERE pm.user_id = %s AND t.status <> 'DONE'
             AND t.deadline BETWEEN CURDATE() AND CURDATE() + INTERVAL 7 DAY
           ORDER BY t.deadline""",
        (user_id,),
    )

    return {"by_status": by_status, "my_tasks": my_tasks, "due_soon": due_soon}
