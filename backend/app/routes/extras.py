import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.crud.extra import create_extra, get_all_extras, update_extra
from app.database import get_session
from app.models import User
from app.schemas.extra import ExtraCreate, ExtraPublic, ExtraUpdate
from app.services.dependencies import get_current_active_user

router = APIRouter(prefix="/extras", tags=["extras"], dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=list[ExtraPublic])
def read_all_extras(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_extras(db, offset=offset, limit=limit)


@router.post("/")
def create_extra_data(data: ExtraCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return create_extra(db, data, current_user.id)


@router.patch("/{extra_id}")
def update_extra_data(extra_id: uuid.UUID, data: ExtraUpdate, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return update_extra(db, extra_id, data, current_user.id)