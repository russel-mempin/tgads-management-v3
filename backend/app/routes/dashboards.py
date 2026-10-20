from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.crud.dashboard import get_owner_dashboard_data
from app.database import get_session
from app.enums import UserRoles
from app.models import User
from app.schemas.dashboard import OwnerDashboard
from app.services.dependencies import get_current_active_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(get_current_active_user)])


@router.get("/owner", response_model=OwnerDashboard)
def read_dashboard_data(db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRoles.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this data."
        )
    return get_owner_dashboard_data(db)