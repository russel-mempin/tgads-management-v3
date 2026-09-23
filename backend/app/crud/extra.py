from sqlmodel import Session, select

from app.models import ExtraService


def get_all_extras(db: Session, offset: int = 0, limit: int = 100) -> list[ExtraService]:
    return list(
        db.exec(
            select(ExtraService)
            .where(ExtraService.is_active == True)
            .offset(offset)
            .limit(limit)
        ).all()
    )