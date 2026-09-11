import uuid
from datetime import datetime
from decimal import Decimal

from sqlmodel import SQLModel

from app.enums import ExpenseCategory
from app.models import ExpenseBase


class ExpensePublic(ExpenseBase):
    id: uuid.UUID
    account_name: str
    
class ExpenseCreate(SQLModel):
    date: datetime
    category: ExpenseCategory
    amount: Decimal
    description: str
    fund_source: uuid.UUID
    
class ExpenseSummary(SQLModel):
    total: Decimal
    count: int
    largest: ExpensePublic | None
    
    
class ExpenseByCategory(SQLModel):
    category: ExpenseCategory
    amount: Decimal
    
    
class ExpenseList(SQLModel):
    items: list[ExpensePublic]
    total_items: int
    summary: ExpenseSummary
    expense_by_category: list[ExpenseByCategory]