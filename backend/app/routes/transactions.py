from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.crud.transaction import get_all_transactions
from app.database import get_session
from app.enums import DatePeriod, TransactionSource
from app.schemas.transaction import TransactionPublic
from app.services.dependencies import get_current_active_user

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/", response_model=list[TransactionPublic])
def read_all_transactions(
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    db: Session = Depends(get_session),
    period: DatePeriod = DatePeriod.ALL,
    source: TransactionSource | None = None,
):
    return get_all_transactions(db, period=period, source=source, offset=offset, limit=limit)
