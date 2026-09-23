import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import AuditLog, Service, ServiceOption, ServicePriceTier
from app.schemas.service import (
    ServiceCreate,
    ServiceOptionCreate,
    ServiceUpdate,
)
from app.utils.utils import validate_price_tiers


def get_all_services(
    db: Session, offset: int = 0, limit: int = 100
) -> list[Service]:
    return list(
        db.exec(
            select(Service)
            .where(Service.is_active == True)
            .offset(offset)
            .limit(limit)
        ).all()
    )
    
    
def get_service_data(db: Session, service_id: uuid.UUID) -> Service:
    service = db.exec(select(Service).where(Service.id == service_id)).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found."
        )
    return service


def create_option(db: Session, data: ServiceOptionCreate, service_id: uuid.UUID, current_user_id: uuid.UUID):
    try:
        service = db.exec(select(Service).where(Service.id == service_id)).first()
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Service not found."
            )
        existing = db.exec(
            select(ServiceOption).where(
                ServiceOption.service_id == service_id,
                ServiceOption.name == data.name,
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Service option with name '{data.name}' already exists.",
            )
        option_data = data.model_dump(exclude={"price_tiers"})
        service_option = ServiceOption(
            **option_data,
            service_id=service.id
        )
        db.add(service_option)
        db.flush()
        if data.price_tiers is not None:
            try:
                validate_price_tiers(data.price_tiers)
                for tier in data.price_tiers:
                    db.add(ServicePriceTier(
                        service_option_id=service_option.id,
                        min_threshold=tier.min_threshold,
                        max_threshold=tier.max_threshold if tier.max_threshold else None,
                        rate=tier.rate
                    ))
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))        
        audit = AuditLog(
            action=f"Added service {service_option.name} under {service.name}", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        return "Service option created."
    except Exception:
        db.rollback()
        raise


def create_service(db: Session, data: ServiceCreate, current_user_id: uuid.UUID):
    try:
        existing = db.exec(
            select(Service).where(
                (Service.name == data.name)
                | (Service.abbreviation == data.abbreviation)
            )
        ).first()
        if existing:
            if existing.name == data.name:
                raise HTTPException(
                    status_code=409,
                    detail=f"Service type with name '{data.name}' already exists.",
                )
            if existing.abbreviation == data.abbreviation:
                raise HTTPException(
                    status_code=409,
                    detail=f"Service type with abbreviation '{data.abbreviation}' already exists.",
                )
        service_type = Service(**data.model_dump())
        db.add(service_type)
        db.commit()
        db.refresh(service_type)

        audit = AuditLog(
            action=f"Created service named {service_type.name}", user_id=current_user_id
        )
        db.add(audit)
        db.commit()

        return service_type
    except Exception:
        db.rollback()
        raise


def update_service(
    db: Session, service_id: uuid.UUID, data: ServiceUpdate, current_user_id: uuid.UUID
):
    try:
        service = db.exec(
            select(Service).where(Service.id == service_id)
        ).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service type not found")

        updated_data = data.model_dump(exclude_unset=True)  # only fields that were sent
        for key, value in updated_data.items():
            setattr(service, key, value)

        db.add(service)

        audit = AuditLog(
            action=f"Updated service {service.name}", user_id=current_user_id
        )
        db.add(audit)

        db.commit()
        db.refresh(service)
        return service
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise


def archive_service(db: Session, service_id: uuid.UUID, current_user_id: uuid.UUID):
    try:
        service = db.exec(
            select(Service).where(Service.id == service_id)
        ).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service type not found")

        service.is_active = False
        db.add(service)

        audit = AuditLog(
            action=f"Deleted service named {service.name}", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        db.refresh(service)
        return "Service deleted."
    except HTTPException:
        raise  # don't rollback for 404s, nothing was changed
    except Exception:
        db.rollback()
        raise