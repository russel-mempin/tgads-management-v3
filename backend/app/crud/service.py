from sqlmodel import Session, select
from app.models import ServiceType
from sqlalchemy import func
from fastapi import HTTPException
from app.schemas.service import ServicePublic

def get_all_service_names(
	db: Session, offset: int = 0, limit: int = 100
) -> list[ServiceType]:
    return list(db.exec(
		select(ServiceType).offset(offset).limit(limit)
	).all())