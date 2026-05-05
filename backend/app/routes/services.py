from fastapi import APIRouter, Query, Depends
from typing import Annotated
from sqlmodel import Session
from app.database import get_session
from app.crud.service import get_all_services, get_all_extras
from app.schemas.service import ServicePublic
from app.models import ExtraType


router = APIRouter(prefix="/services", tags=["services"])


@router.get("/", response_model=list[ServicePublic])
def read_all_services(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_services(db, offset=offset, limit=limit)

@router.get("/extras", response_model=list[ExtraType])
def read_all_extras(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_extras(db, offset=offset, limit=limit)