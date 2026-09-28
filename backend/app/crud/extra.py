import uuid

from sqlmodel import Session, select

from app.models import AuditLog, ExtraService
from app.schemas.extra import ExtraCreate


def get_all_extras(db: Session, offset: int = 0, limit: int = 100) -> list[ExtraService]:
    return list(
        db.exec(
            select(ExtraService)
            .where(ExtraService.is_active == True)
            .offset(offset)
            .limit(limit)
        ).all()
    )


def create_extra(db: Session, data: ExtraCreate, current_user_id: uuid.UUID):
    try:
        existing = db.exec(select(ExtraService).where(ExtraService.name == data.name)).first()
        if existing:
            return "Extra service with this name already exists."
        extra = ExtraService(
            name=data.name,
            price=data.price,
            is_active=data.is_active,
        )
        db.add(extra)
        db.commit()
        db.add(AuditLog(action="Created extra service", user_id=current_user_id))
        db.commit()
        return "Extra service created successfully."
    except Exception:
        db.rollback()
        raise