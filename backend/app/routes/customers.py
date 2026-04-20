from fastapi import APIRouter, Query, Depends
from typing import Annotated
from sqlmodel import Session
from app.database import get_session
from app.crud.customer import get_all_customer_names, get_customer_info
from app.schemas.customer import CustomerPublic


router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/names", response_model=list[str])
def read_all_names(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_customer_names(db, offset=offset, limit=limit)

@router.get("/{name}", response_model=CustomerPublic)
def read_customer_info(name: str, db: Session = Depends(get_session)):
    return get_customer_info(db, name)
    

