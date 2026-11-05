import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.enums import TransactionSource
from app.models import Account, AccountTransaction, AccountTransfer, AuditLog
from app.schemas.transfer import AccountTransferCreate, AccountTransferPublic


def get_all_transfers(db: Session, include_archived: bool = False, search: str | None = None) -> list[AccountTransferPublic]:
    statement = select(AccountTransfer)

    if not include_archived:
        statement = statement.where(AccountTransfer.is_archived.is_(False))

    if search:
        statement = statement.where(
            AccountTransfer.description.ilike(f"%{search}%")
        )
    
    statement = statement.order_by(AccountTransfer.transferred_at.desc())
    return list(db.exec(statement).all())


def create_transfer(db: Session, data: AccountTransferCreate, current_user_id: uuid.UUID):
    try:
        source_account = db.get(Account, data.source_account_id)
        if not source_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selected Source account not found.",
            )
        destination_account = db.get(Account, data.destination_account_id)
        if not destination_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selected Destination account not found.",
            )
        db.add(AccountTransfer(
            transferred_at=data.transferred_at,
            description=data.description,
            reference_number=data.reference_number,
            amount=data.amount,
            source_account_id=data.source_account_id,
            destination_account_id=data.destination_account_id,
            created_by_id=current_user_id,
        ))
        db.add(AccountTransaction(
            account_id=data.source_account_id,
            source_type=TransactionSource.TRANSFER_SOURCE,
            amount=-data.amount,
            reference_number=data.reference_number,
            description=data.description,
            created_by_id=current_user_id,
        ))
        db.add(AccountTransaction(
            account_id=data.destination_account_id,
            source_type=TransactionSource.TRANSFER_DESTINATION,
            amount=data.amount,
            reference_number=data.reference_number,
            description=data.description,
            created_by_id=current_user_id,
        ))
        db.add(AuditLog(
            action=f"Created transfer of {data.amount} from account {source_account.name} to account {destination_account.name}.",
            user_id=current_user_id
        ))
        db.commit()
        return "Transfer saved successfully."
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise