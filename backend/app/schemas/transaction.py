from datetime import datetime
from decimal import Decimal

from sqlmodel import SQLModel

from app.enums import TransactionSource


class TransactionPublic(SQLModel):
    date: datetime
    amount: Decimal
    source_type: TransactionSource
    account_name: str