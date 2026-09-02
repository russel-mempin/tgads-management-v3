import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import AuditLog, MiscSale, MiscSaleBase
from app.schemas.misc_sale import MiscSaleCreate, MiscSalePublic


def get_all_misc_sales(
    db: Session,
    include_archived: bool = False,
    offset: int = 0,
    limit: int = 100,
) -> list[MiscSalePublic]:
    statement = select(MiscSale)

    if not include_archived:
        statement = statement.where(MiscSale.is_archived == False)

    statement = statement.offset(offset).limit(limit)

    return list(db.exec(statement).all())
    
    
def create_misc_sale(db: Session, data: MiscSaleCreate, current_user_id: uuid.UUID):
    try:
        misc_sale = MiscSale(
            date=data.date,
            description=data.description,
            amount=data.amount,
            account_id=data.account_id
        )
        db.add(misc_sale)
        db.commit()
        db.refresh(misc_sale)
        
        audit = AuditLog(
            action="Created misc sale", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        return "Misc. sale data created."
    except Exception:
        db.rollback()
        raise
    
    
def update_misc_sale(db: Session, misc_sale_id: uuid.UUID, data: MiscSaleBase, current_user_id: uuid.UUID):
    try:
        misc_sale = db.exec(
            select(MiscSale).where(MiscSale.id == misc_sale_id)
        ).first()
        if not misc_sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Misc sale not found.")
        
        misc_sale.date = data.date
        misc_sale.description = data.description
        misc_sale.amount = data.amount
        
        db.add(misc_sale)
        db.commit()
        db.refresh(misc_sale)
        
        audit = AuditLog(
            action="Updated misc sale", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        
        return misc_sale
    except Exception:
        db.rollback()
        raise
    
    
def archive_misc_sale(db: Session, misc_sale_id: uuid.UUID, current_user_id: uuid.UUID):
    try:
        misc_sale = db.exec(
            select(MiscSale).where(MiscSale.id == misc_sale_id)
        ).first()
        if not misc_sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Misc sale not found")

        misc_sale.is_archived = True
        db.add(misc_sale)

        audit = AuditLog(
            action=f"Deleted misc_sale {misc_sale.description}", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        db.refresh(misc_sale)
        return "Misc sale deleted."
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise