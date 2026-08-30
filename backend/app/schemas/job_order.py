import uuid
from decimal import Decimal

from sqlmodel import Field, SQLModel

from app.enums import JobStatus, PaymentStatus, PriceUnit
from app.models import ClaimingHistoryBase, JobItemBase, JobOrderBase, PaymentBase


class PricingData(SQLModel):
    consumption: float
    consumption_unit: PriceUnit | None = None
    rate: Decimal
    unit_price: Decimal


class JobItemExtraPublic(SQLModel):
    id: uuid.UUID
    extra_service_id: uuid.UUID
    quantity: int
    price_snapshot: Decimal
    name_snapshot: str
    
    
class JobItemExtraCreate(SQLModel):
    extra_service_id: uuid.UUID
    quantity: int
    

class JobItemPublic(JobItemBase):
    id: uuid.UUID
    total_claimed: int
    remaining_on_hand: int
    extras: list[JobItemExtraPublic] = Field(default_factory=list)
    service_id: uuid.UUID
    service_option_id: uuid.UUID
    unit_price: Decimal
    subtotal: Decimal
    service_name_snapshot: str
    service_option_name_snapshot: str
    service_abbreviation_snapshot: str
    
    
class JobItemCreate(JobItemBase):
    service_id: uuid.UUID
    service_option_id: uuid.UUID
    extras: list[JobItemExtraCreate] = Field(default_factory=list)
    

class JobItemUpdate(SQLModel):
    quantity: int | None = None
    job_status: JobStatus | None = None
    notes: str | None = None
    extra_charge: Decimal | None = None
    discount_amount: Decimal | None = None
    extras: list[JobItemExtraCreate] | None = None
    
    
class PaymentPublic(PaymentBase):
    id: uuid.UUID
    
    
class PaymentCreate(PaymentBase):
    account_id: uuid.UUID


class ClaimPublic(ClaimingHistoryBase):
    job_item_id: uuid.UUID
    
    
class ClaimCreate(ClaimingHistoryBase):
    pass


class JobOrderPublic(JobOrderBase):
    id: uuid.UUID
    job_items: list[JobItemPublic] = Field(default_factory=list)
    payments: list[PaymentPublic] = Field(default_factory=list)
    claiming_history: list[ClaimPublic] = Field(default_factory=list)
    total_due: Decimal
    total_paid: Decimal
    balance: Decimal
    customer_name: str | None = None
    customer_email: str | None = None
    customer_contact_no: str | None = None
    created_by_name: str | None = None
    updated_by_name: str | None = None
    voided_by_name: str | None = None
    void_reason: str | None = None
    

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
    claiming_history: list[ClaimCreate] | None = None