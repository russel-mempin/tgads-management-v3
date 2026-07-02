from sqlmodel import SQLModel
from app.models import ExpenseBase
from app.enums import ExpenseCategory
from datetime import datetime
import uuid

class ExpensePublic(ExpenseBase):
    id: uuid.UUID
    account_name: str
    
class ExpenseCreate(SQLModel):
    date: datetime
    category: ExpenseCategory
    amount: float
    description: str
    fund_source: uuid.UUID