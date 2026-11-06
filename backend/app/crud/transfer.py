import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session, select

from app.enums import ReasonCategory, ReviewEntityType, TransactionSource, UserRoles
from app.models import (
    Account,
    AccountTransaction,
    AccountTransfer,
    AuditLog,
    ForReview,
    User,
)
from app.schemas.transfer import (
    AccountTransferCreate,
    AccountTransferPublic,
    AccountTransferUpdate,
)


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


def update_transfer(
    db: Session,
    transfer_id: uuid.UUID,
    data: AccountTransferUpdate,
    current_user: User,
):
    try:
        transfer = db.get(AccountTransfer, transfer_id, with_for_update=True)

        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found",
            )

        # Save old transaction state BEFORE updating transfer.
        old_amount = transfer.amount
        old_date = transfer.transferred_at
        old_source_account = db.get(Account, transfer.source_account_id)
        old_destination_account = db.get(Account, transfer.destination_account_id)
        old_description = transfer.description

        update_data = data.model_dump(exclude_unset=True)
        old_data = {}
        new_data = {}

        for field, value in update_data.items():
            old_value = getattr(transfer, field)

            if old_value != value:
                old_data[field] = jsonable_encoder(old_value)
                new_data[field] = jsonable_encoder(value)
                setattr(transfer, field, value)

        if not new_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No changes detected.",
            )

        # Validate accounts if changed.
        source_account = db.get(Account, transfer.source_account_id)
        destination_account = db.get(Account, transfer.destination_account_id)

        if not source_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selected Source account not found.",
            )

        if not destination_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selected Destination account not found.",
            )

        if transfer.source_account_id == transfer.destination_account_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source and destination accounts cannot be the same.",
            )

        if transfer.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transfer amount must be greater than zero.",
            )

        transfer.updated_by_id = current_user.id
        transfer.updated_at = datetime.now(UTC)

        # Update transactions if a financial field changed.
        if any(
            field in new_data
            for field in (
                "amount",
                "transferred_at",
                "source_account_id",
                "destination_account_id",
            )
        ):
            # Reverse old outgoing transaction.
            db.add(
                AccountTransaction(
                    date=old_date,
                    amount=old_amount,
                    source_type=TransactionSource.REVERSAL,
                    source_id=transfer.id,
                    account=old_source_account,
                    description=f"Reversal of transfer: {old_description}",
                )
            )

            # Reverse old incoming transaction.
            db.add(
                AccountTransaction(
                    date=old_date,
                    amount=-old_amount,
                    source_type=TransactionSource.REVERSAL,
                    source_id=transfer.id,
                    account=old_destination_account,
                    description=f"Reversal of transfer: {old_description}",
                )
            )

            # Create new outgoing transaction.
            db.add(
                AccountTransaction(
                    date=transfer.transferred_at,
                    amount=-transfer.amount,
                    source_type=TransactionSource.TRANSFER_SOURCE,
                    source_id=transfer.id,
                    account=source_account,
                    description=f"Transfer: {transfer.description}",
                )
            )

            # Create new incoming transaction.
            db.add(
                AccountTransaction(
                    date=transfer.transferred_at,
                    amount=transfer.amount,
                    source_type=TransactionSource.TRANSFER_DESTINATION,
                    source_id=transfer.id,
                    account=destination_account,
                    description=f"Transfer: {transfer.description}",
                )
            )

        if current_user.role != UserRoles.OWNER:
            db.add(
                ForReview(
                    entity_type=ReviewEntityType.TRANSFER,
                    entity_id=transfer.id,
                    entity_reference=transfer.reference_number or None,
                    reason_category=ReasonCategory.EDIT_REQUIRES_APPROVAL,
                    old_data=old_data,
                    new_data=new_data,
                    reason="Transfer edited by non-owner",
                    created_by_id=current_user.id,
                )
            )

        db.add(transfer)

        db.add(
            AuditLog(
                action="Updated transfer",
                user_id=current_user.id,
            )
        )

        db.commit()
        db.refresh(transfer)

        return transfer

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise