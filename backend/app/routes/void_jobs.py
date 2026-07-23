from fastapi import APIRouter, Query, Depends
from typing import Annotated
from app.services.dependencies import get_current_active_user
from sqlmodel import Session
from app.database import get_session
from app.schemas.void_job import VoidJobOrderPublic
from app.crud.void_job import get_all_voided_jobs


router = APIRouter(prefix="/void-jobs", tags=["void-jobs"], dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=list[VoidJobOrderPublic])
def read_all_void_jobs(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_voided_jobs(db, offset=offset, limit=limit)