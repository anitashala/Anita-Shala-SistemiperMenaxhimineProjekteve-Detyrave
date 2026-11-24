from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

from app import config


def _prepare(password: str) -> bytes:
    # bcrypt përdor vetëm 72 bytes të para
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_prepare(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(_prepare(password), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=config.JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")


def decode_access_token(token: str) -> Optional[int]:
    """Kthen ID-në e përdoruesit nga token-i, ose None nëse token-i është i pavlefshëm/skaduar."""
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
