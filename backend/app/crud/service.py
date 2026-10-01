import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import AuditLog, Service, ServiceOption, ServicePriceTier
from app.schemas.service import (
    ServiceCreate,
    ServiceOptionCreate,
    ServiceOptionUpdate,
    ServiceUpdate,
)
from app.utils.utils import validate_price_tiers


def get_all_services(
    db: Session, include_inactive: bool = False, offset: int = 0, limit: int = 100
) -> list[Service]:
    statement = select(Service)
    if not include_inactive:
        statement = statement.where(Service.is_active == True)
    statement = statement.offset(offset).limit(limit)
    return list(db.exec(statement).all())
    
    
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
                status_code=status.HTTP_409_CONFLICT,
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


def update_option(db: Session, data: ServiceOptionUpdate, service_id: uuid.UUID, option_id: uuid.UUID, current_user_id: uuid.UUID):
    try:
        option = db.exec(
            select(ServiceOption)
            .where(
                ServiceOption.id == option_id,
                ServiceOption.service_id == service_id,
            )
        ).first()
        if not option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service option not found",
            )
        update_data = data.model_dump(
            exclude_unset=True,
            exclude={"price_tiers"}
        )
        # Update ServiceOption fields
        for field, value in update_data.items():
            setattr(option, field, value)
            
        # Update price tiers if they were included
        if data.price_tiers is not None:
            option.price_tiers.clear()
            for tier_data in data.price_tiers:
                option.price_tiers.append(
                    ServicePriceTier(
                        service_option_id=option.id,
                        min_threshold=tier_data.min_threshold,
                        max_threshold=tier_data.max_threshold,
                        rate=tier_data.rate,
                    )
                )
        db.add(option)
        db.commit()
        db.refresh(option)

        audit = AuditLog(
            action=f"Created service option named {option.name}", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        
        return option
        
    except Exception:
        db.rollback()
        raise

# Rename everything to deactivate
def archive_option(db: Session, service_id: uuid.UUID, option_id: uuid.UUID, current_user_id: uuid.UUID):
    try:
        option = db.exec(
            select(ServiceOption)
            .where(
                ServiceOption.id == option_id,
                ServiceOption.service_id == service_id,
            )
        ).first()
        if not option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service option not found",
            )
        if option.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service option is already inactive.",
            )
        option.is_active = False
        db.add(option)
        db.add(AuditLog(
            action=f"Archived service option named {option.name}", user_id=current_user_id
        ))
        db.commit()
        return f"Service option {option.name} marked inactive."
    except Exception:
        db.rollback()
        raise


def activate_option(db: Session, service_id: uuid.UUID, option_id: uuid.UUID, current_user_id: uuid.UUID):
    try:
        option = db.exec(
            select(ServiceOption)
            .where(
                ServiceOption.id == option_id,
                ServiceOption.service_id == service_id,
            )
        ).first()
        if not option:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service option not found",
            )
        if option.is_active is True:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service option is already active.",
            )
        option.is_active = True
        db.add(option)
        db.add(AuditLog(
            action=f"Restored service option named {option.name}", user_id=current_user_id
        ))
        db.commit()
        return f"Service option {option.name} marked active."
    except Exception:
        db.rollback()
        raise


def update_service(
    db: Session, data: ServiceUpdate, service_id: uuid.UUID, current_user_id: uuid.UUID
):
    try:
        service = db.exec(
            select(Service).where(Service.id == service_id)
        ).first()
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service type not found")
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
        return "Service updated."
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise


def deactivate_service(db: Session, service_id: uuid.UUID, current_user_id: uuid.UUID):
    try:
        service = db.exec(
            select(Service).where(Service.id == service_id)
        ).first()
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service type not found")
        if not service.is_active:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Service named {service.name} already inactive")
        service.is_active = False
        options = db.exec(
            select(ServiceOption).where(
                ServiceOption.service_id == service_id
            )
        ).all()
        for option in options:
            option.is_active = False
            db.add(option)
        db.add(service)
        audit = AuditLog(
            action=f"Deactivated service named {service.name}", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        db.refresh(service)
        return "Service and related options deactivated."
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise


def reactivate_service(db: Session, service_id: uuid.UUID, current_user_id: uuid.UUID):
    try:
        service = db.exec(
            select(Service).where(Service.id == service_id)
        ).first()
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service type not found")
        if service.is_active:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Service named {service.name} already active")
        service.is_active = True
        db.add(service)
        audit = AuditLog(
            action=f"Reactivated service named {service.name}", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        db.refresh(service)
        return f"Service named {service.name} reactivated."
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise


def create_service(db: Session, service_data: ServiceCreate, current_user_id: uuid.UUID):
    try:
        existing_name = db.exec(
            select(Service).where(Service.name == service_data.name)
        ).first()
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Service with name '{service_data.name}' already exists.",
            )
        existing_abbreviation = db.exec(
            select(Service).where(Service.abbreviation == service_data.abbreviation)
        ).first()
        if existing_abbreviation:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Service with abbreviation '{service_data.abbreviation}' already exists.",
            )
        service = Service(
            name=service_data.name,
            abbreviation=service_data.abbreviation,
            pricing_strategy=service_data.pricing_strategy,
            unit=service_data.unit,
        )
        db.add(service)
        db.flush()

        for option_data in service_data.options:
            existing_option = db.exec(
                select(ServiceOption).where(
                    ServiceOption.service_id == service.id,
                    ServiceOption.name == option_data.name,
                )
            ).first()
            if existing_option:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Service option with name '{option_data.name}' already exists.",
                )
            service_option = ServiceOption(
                name=option_data.name,
                base_rate=option_data.base_rate,
                is_active=option_data.is_active,
                minimum_consumption=option_data.minimum_consumption,
                stock_increment=option_data.stock_increment,
                service_id=service.id
            )
            db.add(service_option)
            db.flush()

            if option_data.price_tiers is not None:
                try:
                    validate_price_tiers(option_data.price_tiers)
                    for tier in option_data.price_tiers:
                        db.add(ServicePriceTier(
                            service_option_id=service_option.id,
                            min_threshold=tier.min_threshold,
                            max_threshold=tier.max_threshold if tier.max_threshold else None,
                            rate=tier.rate
                        ))
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=str(e))
        audit = AuditLog(
            action=f"Created service {service.name} with options", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        return "Service and options created."
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise