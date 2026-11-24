from fastapi import APIRouter, Depends

from app.db.database import get_db
from app.schemas.schemas import LoginIn, RegisterIn
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", status_code=201)
def register(data: RegisterIn, db=Depends(get_db)):
    return auth_service.register(db, data)


@router.post("/login")
def login(data: LoginIn, db=Depends(get_db)):
    return auth_service.login(db, data)
