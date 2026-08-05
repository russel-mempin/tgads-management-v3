import uuid

from sqlmodel import Field, SQLModel

from app.enums import PaymentStatus, PriceUnit
from app.models import ClaimingHistoryBase, JobItemBase, JobOrderBase, PaymentBase


class PricingData(SQLModel):
    consumption: float
    consumption_unit: PriceUnit | None = None
    rate: float
    unit_price: float


class JobItemExtraPublic(SQLModel):
    id: uuid.UUID
    extra_service_id: uuid.UUID
    quantity: int
    price_snapshot: float
    name_snapshot: str
    

class JobItemPublic(JobItemBase):
    id: uuid.UUID
    total_claimed: int
    remaining_on_hand: int
    extras: list[JobItemExtraPublic] = Field(default_factory=list)
    
    
class JobItemCreate(JobItemBase):
    pass
    
    
class PaymentPublic(PaymentBase):
    id: uuid.UUID
    
    
class PaymentCreate(PaymentBase):
    pass


class ClaimPublic(ClaimingHistoryBase):
    job_item_id: uuid.UUID
    
    
class ClaimCreate(ClaimingHistoryBase):
    pass


class JobOrderPublic(JobOrderBase):
    id: uuid.UUID
    job_items: list[JobItemPublic] = Field(default_factory=list)
    payments: list[PaymentPublic] = Field(default_factory=list)
    claims: list[ClaimPublic] = Field(default_factory=list)
    total_due: float
    total_paid: float
    customer_name: str | None = None
    customer_email: str | None = None
    customer_contact_no: str | None = None
    created_by_name: str | None = None
    updated_by_name: str | None = None
    

class CustomerReference(SQLModel):
    id: uuid.UUID | None = None
    name: str | None = None
    address: str | None = None
    contact_no: str | None = None
    email: str | None = None

    
class JobOrderCreate(JobOrderBase):
    override_payment_status: PaymentStatus | None = None
    customer_info: CustomerReference | None = None
    job_items: list[JobItemCreate] = Field(default_factory=list)
    payments: list[PaymentCreate] | None = None
    claims: list[ClaimCreate] | None = None