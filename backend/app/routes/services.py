import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.crud.service import (
    activate_option,
    archive_option,
    create_option,
    deactivate_service,
    get_all_services,
    get_service_data,
    reactivate_service,
    update_option,
    update_service,
)
from app.database import get_session
from app.models import User
from app.schemas.service import (
    ServiceOptionCreate,
    ServiceOptionUpdate,
    ServicePublic,
    ServiceUpdate,
)
from app.services.dependencies import get_current_active_user

router = APIRouter(prefix="/services", tags=["services"], dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=list[ServicePublic])
def read_all_services(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_services(db, offset=offset, limit=limit)


@router.get("/{service_id}", response_model=ServicePublic)
def read_service(service_id: uuid.UUID, db: Session = Depends(get_session)):
    return get_service_data(db, service_id)


@router.post("/{service_id}/options/")
def create_option_data(data: ServiceOptionCreate, service_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return create_option(db, data, service_id, current_user.id)


@router.patch("/{service_id}/options/{option_id}")
def update_option_data(data: ServiceOptionUpdate, service_id: uuid.UUID, option_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return update_option(db, data, service_id, option_id, current_user.id)


@router.patch("/{service_id}/options/{option_id}/archive")
def archive_option_data(service_id: uuid.UUID, option_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return archive_option(db, service_id, option_id, current_user.id)


@router.patch("/{service_id}/options/{option_id}/activate")
def activate_option_data(service_id: uuid.UUID, option_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return activate_option(db, service_id, option_id, current_user.id)


@router.patch("/{service_id}")
def update_service_data(data: ServiceUpdate, service_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return update_service(db, data, service_id, current_user.id)


@router.patch("/{service_id}/deactivate")
def deactivate_service_data(service_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return deactivate_service(db, service_id, current_user.id)


@router.patch("/{service_id}/reactivate")
def reactivate_service_data(service_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return reactivate_service(db, service_id, current_user.id)