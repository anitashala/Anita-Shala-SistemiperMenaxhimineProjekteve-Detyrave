from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db.database import fetch_one, get_db
from app.errors import AppError
from app.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db=Depends(get_db),
):
    """Verifikon JWT-në nga header-i Authorization dhe kthen përdoruesin aktual."""
    if credentials is None:
        raise AppError(401, "NOT_AUTHENTICATED", "Authentication required.")

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise AppError(401, "NOT_AUTHENTICATED", "Invalid or expired token.")

    user = fetch_one(
        db, "SELECT id, full_name, email, role FROM users WHERE id = %s", (user_id,)
    )
    if user is None:
        raise AppError(401, "NOT_AUTHENTICATED", "User no longer exists.")
    return user
