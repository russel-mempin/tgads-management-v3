import uuid

from app.models import AccountTransferBase


class AccountTransferPublic(AccountTransferBase):
    id: uuid.UUID
    source_account_name: str
    destination_account_name: str
    created_by_name: str
    updated_by_name: str | None = None
    voided_by_name: str | None = None