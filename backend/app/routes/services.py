from fastapi import APIRouter, Query, Depends
from typing import Annotated
from sqlmodel import Session
from app.database import get_session
from app.crud.service import get_all_service_names
from app.schemas.service import ServicePublic


router = APIRouter(prefix="/services", tags=["services"])


@router.get("/names", response_model=list[ServicePublic])
def read_all_names(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_service_names(db, offset=offset, limit=limit)