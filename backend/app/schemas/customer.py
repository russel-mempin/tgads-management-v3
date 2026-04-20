from app.models import CustomerBase
import uuid


class CustomerPublic(CustomerBase):
    id: uuid.UUID