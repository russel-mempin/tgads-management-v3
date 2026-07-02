from fastapi import APIRouter, Query, Depends
from typing import Annotated
from sqlmodel import Session
from app.database import get_session
from app.crud.account import get_all_account_names
from app.services.dependencies import get_current_active_user
from app.schemas.account import AccountOption


router = APIRouter(prefix="/accounts", tags=["accounts"], dependencies=[Depends(get_current_active_user)])


@router.get("/options", response_model=list[AccountOption])
def read_all_account_options(db: Session = Depends(get_session)):
    return get_all_account_names(db)
