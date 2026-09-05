import uuid
from datetime import datetime
from decimal import Decimal

from sqlmodel import SQLModel

from app.models import MiscSaleBase


class MiscSalePublic(MiscSaleBase):
    id: uuid.UUID
    account_name: str
    
class MiscSaleCreate(MiscSaleBase):
    account_id: uuid.UUID
    
    
class MiscSaleUpdate(SQLModel):
    amount: Decimal | None = None
    date: datetime | None = None
    reference_number: str | None = None
    account_id: uuid.UUID | None = None
    description: str | None = None