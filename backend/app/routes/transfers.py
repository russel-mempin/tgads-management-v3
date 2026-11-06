import uuid

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.crud.transfer import (
    archive_transfer,
    create_transfer,
    get_all_transfers,
    update_transfer,
)
from app.database import get_session
from app.models import User
from app.schemas.transfer import (
    AccountTransferCreate,
    AccountTransferPublic,
    AccountTransferUpdate,
)
from app.services.dependencies import get_current_active_user

router = APIRouter(
    prefix="/transfers", tags=["transfers"]
)

@router.get("/", response_model=list[AccountTransferPublic])
def read_all_transfers(db: Session = Depends(get_session), include_archived: bool = False, search: str | None = None, current_user: User = Depends(get_current_active_user)):
    return get_all_transfers(db, include_archived=include_archived, search=search)


@router.post("/")
def create(data: AccountTransferCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return create_transfer(db, data, current_user.id)


@router.patch("/{transfer_id}", response_model=AccountTransferPublic)
def update(transfer_id: uuid.UUID, data: AccountTransferUpdate, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return update_transfer(db, transfer_id, data, current_user)


@router.patch("/{transfer_id}/archive")
def archive(transfer_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return archive_transfer(db, transfer_id, current_user)