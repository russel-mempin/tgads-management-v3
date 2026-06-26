from sqlmodel import Session, select
from app.models import MiscSale, MiscSaleBase, AuditLog
import uuid
from fastapi import HTTPException


def get_all_misc_sales(
    db: Session, offset: int = 0, limit: int = 100
) -> list[MiscSale]:
    return list(db.exec(
        select(MiscSale)
        .where(MiscSale.is_archived == False)
        .offset(offset)
        .limit(limit)
    ).all())
    
def create_misc_sale(db: Session, data: MiscSaleBase, current_user_id: uuid.UUID):
    try:
        misc_sale = MiscSale(
            date=data.date,
            description=data.description,
            amount=data.amount
        )
        db.add(misc_sale)
        db.commit()
        db.refresh(misc_sale)
        
        audit = AuditLog(
            action=f"Created misc sale", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        
        return misc_sale
    except Exception:
        db.rollback()
        raise
    
    
def update_misc_sale(db: Session, misc_sale_id: uuid.UUID, data: MiscSaleBase, current_user_id: uuid.UUID):
    try:
        misc_sale = db.exec(
            select(MiscSale).where(MiscSale.id == misc_sale_id)
        ).first()
        if not misc_sale:
            raise HTTPException(status_code=404, detail="Misc sale not found.")
        
        misc_sale.date = data.date
        misc_sale.description = data.description
        misc_sale.amount = data.amount
        
        db.add(misc_sale)
        db.commit()
        db.refresh(misc_sale)
        
        audit = AuditLog(
            action=f"Updated misc sale", user_id=current_user_id
        )
        db.add(audit)
        db.commit()
        
        return misc_sale
    except Exception:
        db.rollback()
        raise