from sqlmodel import Session, select
from app.models import ServiceType, ExtraType

def get_all_services(
	db: Session, offset: int = 0, limit: int = 100
) -> list[ServiceType]:
    return list(db.exec(
		select(ServiceType).offset(offset).limit(limit)
	).all())
    
def get_all_extras(
	db: Session, offset: int = 0, limit: int = 100
) -> list[ExtraType]:
    return list(db.exec(
		select(ExtraType).offset(offset).limit(limit)
	).all())