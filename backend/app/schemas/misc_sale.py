import uuid

from app.models import MiscSaleBase


class MiscSalePublic(MiscSaleBase):
    id: uuid.UUID
    account_name: str
    
class MiscSaleCreate(MiscSaleBase):
    account_id: uuid.UUID