import uuid
from datetime import datetime
from decimal import Decimal

from sqlmodel import SQLModel

from app.models import AccountTransferBase


class AccountTransferPublic(AccountTransferBase):
    id: uuid.UUID
    source_account_name: str
    destination_account_name: str
    created_by_name: str
    updated_by_name: str | None = None
    voided_by_name: str | None = None


class AccountTransferCreate(AccountTransferBase):
    pass


class AccountTransferUpdate(SQLModel):
    reference_number: str | None = None
    description: str | None = None
    amount: Decimal | None = None
    transferred_at: datetime | None = None
    source_account_id: uuid.UUID | None = None
    destination_account_id: uuid.UUID | None = None