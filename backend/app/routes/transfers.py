from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.crud.transfer import get_all_transfers
from app.database import get_session
from app.models import User
from app.schemas.transfer import AccountTransferPublic
from app.services.dependencies import get_current_active_user

router = APIRouter(
    prefix="/transfers", tags=["transfers"]
)

@router.get("/", response_model=list[AccountTransferPublic])
def read_all_transfers(db: Session = Depends(get_session), include_archived: bool = False, search: str | None = None, current_user: User = Depends(get_current_active_user)):
    return get_all_transfers(db, include_archived=include_archived, search=search)