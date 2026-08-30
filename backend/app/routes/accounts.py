from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.crud.account import get_all_account_data, get_all_account_names
from app.database import get_session
from app.schemas.account import AccountOption, AccountPublic
from app.services.dependencies import get_current_active_user

router = APIRouter(prefix="/accounts", tags=["accounts"], dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=list[AccountPublic])
def read_all_account_data(db: Session = Depends(get_session)):
    return get_all_account_data(db)


@router.get("/options", response_model=list[AccountOption])
def read_all_account_options(db: Session = Depends(get_session)):
    return get_all_account_names(db)