import uuid

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from sqlmodel import Session, select

from app.enums import (
    DatePeriod,
    ReasonCategory,
    ReviewEntityType,
    TransactionSource,
    UserRoles,
)
from app.models import Account, AccountTransaction, AuditLog, ForReview, MiscSale, User
from app.schemas.misc_sale import MiscSaleCreate, MiscSalePublic, MiscSaleUpdate
from app.utils.utils import get_date_range


def get_all_misc_sales(
    db: Session,
    include_archived: bool = False,
    search: str | None = None,
    date_period: DatePeriod = DatePeriod.ALL,
    offset: int = 0,
    limit: int = 100,
) -> list[MiscSalePublic]:
    statement = select(MiscSale)

    if not include_archived:
        statement = statement.where(MiscSale.is_archived.is_(False))

    if search:
        statement = statement.where(
            MiscSale.description.ilike(f"%{search}%")
        )

    date_range = get_date_range(date_period)

    if date_range:
        start, end = date_range
        statement = statement.where(
            MiscSale.date >= start,
            MiscSale.date < end,
        )

    statement = statement.order_by(MiscSale.date.desc())
    statement = statement.offset(offset).limit(limit)

    return list(db.exec(statement).all())


def get_misc_sales_count(
    db: Session,
    include_archived: bool = False,
    search: str | None = None,
    date_period: DatePeriod = DatePeriod.ALL,
) -> int:
    statement = select(func.count()).select_from(MiscSale)

    if not include_archived:
        statement = statement.where(MiscSale.is_archived.is_(False))

    if search:
        statement = statement.where(
            MiscSale.description.ilike(f"%{search}%")
        )

    date_range = get_date_range(date_period)

    if date_range:
        start, end = date_range
        statement = statement.where(
            MiscSale.date >= start,
            MiscSale.date < end,
        )

    return db.exec(statement).one()


def create_misc_sale(db: Session, data: MiscSaleCreate, current_user_id: uuid.UUID):
    try:
        account = db.exec(select(Account).where(Account.id == data.account_id)).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found."
            )
        misc_sale = MiscSale(
            date=data.date,
            description=data.description,
            amount=data.amount,
            reference_number=data.reference_number,
            account_id=account.id,
            account_name_snapshot=account.name,
            created_by_id=current_user_id
        )
        db.add(misc_sale)
        db.commit()
        db.refresh(misc_sale)
        db.add(AccountTransaction(
                date=misc_sale.date,
                amount=misc_sale.amount,
                source_type=TransactionSource.MISC_SALE,
                source_id=misc_sale.id,
                account=misc_sale.account,
                description=f"Misc sale: {misc_sale.description}"
        ))
        audit = AuditLog(action="Created misc sale", user_id=current_user_id)
        db.add(audit)
        db.commit()
        return "Misc. sale data created."
    except Exception:
        db.rollback()
        raise


def update_misc_sale(
    db: Session,
    misc_sale_id: uuid.UUID,
    data: MiscSaleUpdate,
    current_user: User,
):
    misc_sale = db.get(MiscSale, misc_sale_id, with_for_update=True)
    if not misc_sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Misc sale not found",
        )

    # Save old transaction state BEFORE updating misc_sale
    old_amount = misc_sale.amount
    old_date = misc_sale.date
    old_account = misc_sale.account

    update_data = data.model_dump(exclude_unset=True)
    old_data = {}
    new_data = {}

    for field, value in update_data.items():
        old_value = getattr(misc_sale, field)

        if old_value != value:
            old_data[field] = jsonable_encoder(old_value)
            new_data[field] = jsonable_encoder(value)
            setattr(misc_sale, field, value)

    if not new_data:
        return misc_sale
    misc_sale.updated_by_id = current_user.id

    # If account/payment method changed, get the new account
    if "account_id" in new_data:
        new_account = db.get(Account, misc_sale.account_id)

        if not new_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )

        misc_sale.account_name_snapshot = new_account.name

    # Update transaction if a financial field changed
    if any(field in new_data for field in ("amount", "date", "account_id")):
        # Reverse old transaction
        db.add(
            AccountTransaction(
                date=old_date,
                amount=-old_amount,
                source_type=TransactionSource.REVERSAL,
                source_id=misc_sale.id,
                account=old_account,
                description=f"Reversal of misc sale: {misc_sale.description}"
            )
        )

        # Create transaction for new state
        db.add(
            AccountTransaction(
                date=misc_sale.date,
                amount=misc_sale.amount,
                source_type=TransactionSource.MISC_SALE,
                source_id=misc_sale.id,
                account=misc_sale.account,
                description=f"Misc sale: {misc_sale.description}"
            )
        )

    if current_user.role != UserRoles.OWNER:
        db.add(
            ForReview(
                entity_type=ReviewEntityType.MISC_SALE,
                entity_id=misc_sale.id,
                entity_reference=misc_sale.reference_number or None,
                reason_category=ReasonCategory.EDIT_REQUIRES_APPROVAL,
                old_data=old_data,
                new_data=new_data,
                reason="Misc sale edited by non-owner",
                created_by_id=current_user.id,
            )
        )

    db.add(misc_sale)
    audit = AuditLog(action="Updated misc sale", user_id=current_user.id)
    db.add(audit)
    db.commit()
    db.refresh(misc_sale)

    return misc_sale


def archive_misc_sale(db: Session, misc_sale_id: uuid.UUID, current_user: User):
    try:
        misc_sale = db.exec(select(MiscSale).where(MiscSale.id == misc_sale_id)).first()
        if not misc_sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Misc sale not found"
            )
        if misc_sale.is_archived:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Misc sale already archived.",
            )
        if misc_sale.created_by_id != current_user.id and current_user.role != UserRoles.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to archive this misc sale.",
            )
        old_archived = misc_sale.is_archived

        misc_sale.is_archived = True
        db.add(misc_sale)
        if current_user.role != UserRoles.OWNER:
            db.add(
                ForReview(
                    entity_type=ReviewEntityType.MISC_SALE,
                    entity_id=misc_sale.id,
                    entity_reference=misc_sale.reference_number or None,
                    reason_category=ReasonCategory.EDIT_REQUIRES_APPROVAL,
                    old_data={"is_archived": old_archived},
                    new_data={"is_archived": True},
                    reason="Misc sale edited by non-owner",
                    created_by_id=current_user.id,
                )
            )
        db.add(
            AccountTransaction(
                date=misc_sale.date,
                amount=-misc_sale.amount,
                source_type=TransactionSource.REVERSAL,
                source_id=misc_sale.id,
                account=misc_sale.account,
                description=f"Reversal of misc sale: {misc_sale.description} due to archiving."
            )
        )

        audit = AuditLog(
            action=f"Archived misc_sale {misc_sale.description} and reversed transaction",
            user_id=current_user.id,
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
