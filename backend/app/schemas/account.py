import uuid
from datetime import datetime
from decimal import Decimal

from sqlmodel import SQLModel

from app.enums import AccountType


class AccountPublic(SQLModel):
    id: uuid.UUID
    name: str
    type: AccountType
    beginning_balance: Decimal
    beginning_balance_date: datetime
    is_active: bool
    current_balance: Decimal


class AccountOption(SQLModel):
    id: uuid.UUID
    name: str