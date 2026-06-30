from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session
from datetime import datetime
from app.database import get_session
from app.crud.report import get_daily_report
from app.services.dependencies import get_current_active_user
from app.models import User
from app.enums import UserRoles

router = APIRouter(prefix="/reports", tags=["reports"], dependencies=[Depends(get_current_active_user)])


@router.get("/daily")
def read_daily_report(
    date: datetime = Query(default_factory=datetime.now),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in [UserRoles.OWNER, UserRoles.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to view this report")
    return get_daily_report(db, date)