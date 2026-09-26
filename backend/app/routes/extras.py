from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.crud.extra import get_all_extras
from app.database import get_session
from app.schemas.extra import ExtraPublic
from app.services.dependencies import get_current_active_user

router = APIRouter(prefix="/extras", tags=["extras"], dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=list[ExtraPublic])
def read_all_extras(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_extras(db, offset=offset, limit=limit)