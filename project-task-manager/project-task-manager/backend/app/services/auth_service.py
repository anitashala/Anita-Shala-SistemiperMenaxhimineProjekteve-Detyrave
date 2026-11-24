from app.db.database import execute, fetch_one
from app.errors import AppError
from app.security import create_access_token, hash_password, verify_password


def register(db, data):
    email = data.email.lower()
    if fetch_one(db, "SELECT id FROM users WHERE email = %s", (email,)):
        raise AppError(409, "EMAIL_ALREADY_EXISTS", "This email is already registered.")

    user_id = execute(
        db,
        "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)",
        (data.full_name, email, hash_password(data.password)),
    )
    return {"id": user_id, "full_name": data.full_name, "email": email, "role": "USER"}


def login(db, data):
    user = fetch_one(
        db,
        "SELECT id, password_hash FROM users WHERE email = %s",
        (data.email.strip().lower(),),
    )
    # Mesazh i njëjtë për email të gabuar dhe fjalëkalim të gabuar
    if user is None or not verify_password(data.password, user["password_hash"]):
        raise AppError(401, "INVALID_CREDENTIALS", "Invalid email or password.")
    return {"access_token": create_access_token(user["id"]), "token_type": "bearer"}
