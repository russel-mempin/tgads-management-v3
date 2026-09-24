import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.crud.service import (
    create_option,
    create_service,
    get_all_services,
    get_service_data,
    update_option,
)
from app.database import get_session
from app.models import User
from app.schemas.service import (
    ServiceCreate,
    ServiceOptionCreate,
    ServicePublic,
)
from app.services.dependencies import get_current_active_user

router = APIRouter(prefix="/services", tags=["services"], dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=list[ServicePublic])
def read_all_services(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_services(db, offset=offset, limit=limit)


@router.get("/{service_id}", response_model=ServicePublic)
def read_service(service_id: uuid.UUID, db: Session = Depends(get_session)):
    return get_service_data(db, service_id)


@router.post("/", response_model=ServicePublic)
def create(data: ServiceCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return create_service(db, data, current_user.id)


@router.post("/{service_id}/options/")
def create_option_data(data: ServiceOptionCreate, service_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return create_option(db, data, service_id, current_user.id)


@router.patch("/{service_id}/option")
def update_option_data(data: ServiceOptionCreate, service_id: uuid.UUID, option_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return update_option(db, data, service_id, option_id, current_user.id)