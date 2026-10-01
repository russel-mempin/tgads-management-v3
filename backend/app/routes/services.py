import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.crud.service import (
    activate_option,
    archive_option,
    create_option,
    create_service,
    deactivate_service,
    get_all_services,
    get_service_data,
    reactivate_service,
    update_option,
    update_service,
)
from app.database import get_session
from app.enums import UserRoles
from app.models import User
from app.schemas.service import (
    ServiceCreate,
    ServiceOptionCreate,
    ServiceOptionUpdate,
    ServicePublic,
    ServiceUpdate,
)
from app.services.dependencies import get_current_active_user

router = APIRouter(prefix="/services", tags=["services"], dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=list[ServicePublic])
def read_all_services(
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    db: Session = Depends(get_session),
    include_inactive: bool = False,
    current_user: User = Depends(get_current_active_user),
):
    if include_inactive and current_user.role == UserRoles.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to do this action."
        )
    return get_all_services(db, include_inactive=include_inactive, offset=offset, limit=limit)


@router.get("/{service_id}", response_model=ServicePublic)
def read_service(service_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRoles.OWNER and current_user.role != UserRoles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to do this action."
        )
    return get_service_data(db, service_id)


@router.post("/{service_id}/options/")
def create_option_data(data: ServiceOptionCreate, service_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRoles.OWNER and current_user.role != UserRoles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to do this action."
        )
    return create_option(db, data, service_id, current_user.id)


@router.patch("/{service_id}/options/{option_id}")
def update_option_data(data: ServiceOptionUpdate, service_id: uuid.UUID, option_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRoles.OWNER and current_user.role != UserRoles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to do this action."
        )
    return update_option(db, data, service_id, option_id, current_user.id)


@router.patch("/{service_id}/options/{option_id}/archive")
def archive_option_data(service_id: uuid.UUID, option_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRoles.OWNER and current_user.role != UserRoles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to do this action."
        )
    return archive_option(db, service_id, option_id, current_user.id)


@router.patch("/{service_id}/options/{option_id}/activate")
def activate_option_data(service_id: uuid.UUID, option_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRoles.OWNER and current_user.role != UserRoles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to do this action."
        )
    return activate_option(db, service_id, option_id, current_user.id)


@router.patch("/{service_id}")
def update_service_data(data: ServiceUpdate, service_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRoles.OWNER and current_user.role != UserRoles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to do this action."
        )
    return update_service(db, data, service_id, current_user.id)


@router.patch("/{service_id}/deactivate")
def deactivate_service_data(service_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRoles.OWNER and current_user.role != UserRoles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to do this action."
        )
    return deactivate_service(db, service_id, current_user.id)


@router.patch("/{service_id}/reactivate")
def reactivate_service_data(service_id: uuid.UUID, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRoles.OWNER and current_user.role != UserRoles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to do this action."
        )
    return reactivate_service(db, service_id, current_user.id)


@router.post("/")
def create_service_data(service_data: ServiceCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRoles.OWNER and current_user.role != UserRoles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to do this action."
        )
    return create_service(db, service_data, current_user.id)