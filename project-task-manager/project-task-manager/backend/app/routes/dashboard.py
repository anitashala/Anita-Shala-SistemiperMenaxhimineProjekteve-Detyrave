from fastapi import APIRouter, Depends

from app.db.database import get_db
from app.dependencies import get_current_user
from app.services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("")
def get_dashboard(db=Depends(get_db), user=Depends(get_current_user)):
    return dashboard_service.get_dashboard(db, user)
