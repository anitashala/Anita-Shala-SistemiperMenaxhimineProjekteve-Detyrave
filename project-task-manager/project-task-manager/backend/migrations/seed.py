"""Plotëson databazën me të dhëna testuese.

Ekzekutimi (nga dosja backend, pasi është krijuar skema dhe .env):
    python migrations/seed.py

Fjalëkalimi i të tre përdoruesve testues: Test1234!
"""
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mysql.connector  # noqa: E402

from app import config  # noqa: E402
from app.security import hash_password  # noqa: E402

PASSWORD = "Test1234!"

connection = mysql.connector.connect(
    host=config.DB_HOST,
    port=config.DB_PORT,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    database=config.DB_NAME,
)
cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'ana@test.com'")
if cursor.fetchone()[0] > 0:
    print("Të dhënat testuese ekzistojnë tashmë. Asgjë nuk u shtua.")
    sys.exit(0)

password_hash = hash_password(PASSWORD)
today = date.today()


def insert(sql, params):
    cursor.execute(sql, params)
    return cursor.lastrowid


# Përdoruesit
ana = insert(
    "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)",
    ("Ana Krasniqi", "ana@test.com", password_hash),
)
beni = insert(
    "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)",
    ("Beni Hoxha", "beni@test.com", password_hash),
)
clara = insert(
    "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)",
    ("Clara Berisha", "clara@test.com", password_hash),
)

# Projektet: Projekti 1 (Owner Ana, anëtar Beni), Projekti 2 (Owner Clara, anëtare Ana)
p1 = insert(
    "INSERT INTO projects (owner_id, name, description, deadline) VALUES (%s, %s, %s, %s)",
    (ana, "Website i ri", "Faqja e re e kompanisë", today + timedelta(days=30)),
)
p2 = insert(
    "INSERT INTO projects (owner_id, name, description, deadline) VALUES (%s, %s, %s, %s)",
    (clara, "Aplikacion mobil", "Prototipi i aplikacionit", today + timedelta(days=60)),
)

members = [(p1, ana, "OWNER"), (p1, beni, "MEMBER"), (p2, clara, "OWNER"), (p2, ana, "MEMBER")]
for project_id, user_id, role in members:
    cursor.execute(
        "INSERT INTO project_members (project_id, user_id, member_role) VALUES (%s, %s, %s)",
        (project_id, user_id, role),
    )

# Detyrat
task_sql = (
    "INSERT INTO tasks (project_id, assigned_to, created_by, title, description, status, priority, deadline) "
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
)
t1 = insert(task_sql, (p1, beni, ana, "Dizajno faqen e login-it", "Skicë dhe HTML/CSS", "IN_PROGRESS", "HIGH", today + timedelta(days=3)))
t2 = insert(task_sql, (p1, ana, ana, "Shkruaj përmbajtjen e faqes kryesore", None, "TODO", "MEDIUM", today + timedelta(days=6)))
t3 = insert(task_sql, (p1, ana, ana, "Konfiguro databazën", None, "DONE", "HIGH", today - timedelta(days=2)))
t4 = insert(task_sql, (p1, None, ana, "Testo formën e kontaktit", "Detyrë e pacaktuar", "TODO", "LOW", None))
t5 = insert(task_sql, (p2, ana, clara, "Skicë e ekraneve", None, "TODO", "MEDIUM", today + timedelta(days=10)))

# Komentet
comment_sql = "INSERT INTO comments (task_id, author_id, content) VALUES (%s, %s, %s)"
cursor.execute(comment_sql, (t1, ana, "A mund ta përfundosh deri të enjten?"))
cursor.execute(comment_sql, (t1, beni, "Po, jam duke e përfunduar."))
cursor.execute(comment_sql, (t3, ana, "Përfundoi, faleminderit!"))

connection.commit()
cursor.close()
connection.close()
print("U shtuan 3 përdorues, 2 projekte, 5 detyra dhe 3 komente.")
print("Hyrja: ana@test.com / beni@test.com / clara@test.com, fjalëkalimi: " + PASSWORD)
