from sqlmodel import Session, select
from app.models import VoidJobOrder


def get_all_voided_jobs(
    db: Session, offset: int = 0, limit: int = 100
) -> list[VoidJobOrder]:
    return list(db.exec(select(VoidJobOrder).offset(offset).limit(limit)).all())
