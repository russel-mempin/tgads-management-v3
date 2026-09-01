import uuid
from datetime import datetime

from sqlmodel import SQLModel

from app.enums import ExpenseCategory
from app.models import ExpenseBase


class ExpensePublic(ExpenseBase):
    id: uuid.UUID
    account_name: str
    
class ExpenseCreate(SQLModel):
    date: datetime
    category: ExpenseCategory
    amount: float
    description: str
    fund_source: uuid.UUID