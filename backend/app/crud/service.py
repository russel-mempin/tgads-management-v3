from sqlmodel import Session, select
from app.models import ServiceType

def get_all(
	db: Session, offset: int = 0, limit: int = 100
) -> list[ServiceType]:
    return list(db.exec(
		select(ServiceType).offset(offset).limit(limit)
	).all())