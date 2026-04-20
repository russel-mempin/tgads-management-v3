from sqlmodel import Session, select
from app.models import Customer
from fastapi import HTTPException
from sqlalchemy import func


def get_all_customer_names(
	db: Session, offset: int = 0, limit: int = 100
) -> list[str]:
    customer_names = list(db.exec(
		select(Customer.name).offset(offset).limit(limit)
	).all())
    return customer_names

def get_customer_info(
	db: Session, name: str
) -> Customer:
    customer = db.exec(select(Customer).where(func.lower(Customer.name) == name.lower())).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer named {name} not found.")
    return customer