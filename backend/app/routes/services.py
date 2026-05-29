from fastapi import APIRouter, Query, Depends
from typing import Annotated
from sqlmodel import Session
from app.database import get_session
from app.crud.service import get_all_services, get_all_extras, create_service, update_service, archive_service, create_extra, update_extra, archive_extra
from app.schemas.service import ServicePublic, ServiceCreate, ServiceUpdate, ExtraCreate, ExtraPublic
from app.models import ExtraType, User
from app.services.dependencies import get_current_active_user
import uuid

router = APIRouter(prefix="/services", tags=["services"], dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=list[ServicePublic])
def read_all_services(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_services(db, offset=offset, limit=limit)

@router.get("/extras", response_model=list[ExtraType])
def read_all_extras(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, db: Session = Depends(get_session)):
    return get_all_extras(db, offset=offset, limit=limit)

@router.post("/", response_model=ServicePublic)
def create(data: ServiceCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return create_service(db, data, current_user.id)

@router.patch("/{service_id}", response_model=ServicePublic)
def update(service_id: uuid.UUID, data: ServiceUpdate, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return update_service(db, service_id, data, current_user.id)

@router.patch("/{service_id}/archive")
def archive(service_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return archive_service(db, service_id, current_user.id)

@router.post("/extras", response_model=ExtraPublic)
def create_extra_service(data: ExtraCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return create_extra(db, data, current_user.id)

@router.put("/extras/{extra_id}", response_model=ExtraPublic)
def update_extra_service(extra_id: uuid.UUID, data: ExtraCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return update_extra(db, extra_id, data, current_user.id)

@router.patch("/extras/{extra_id}/archive")
def archive_extra_service(extra_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    return archive_extra(db, extra_id, current_user.id)