from app.models import JobItemBase, PaymentBase, ClaimingHistoryBase, JobOrderBase, PaymentStatus
from sqlmodel import Field
import uuid
from datetime import datetime, timezone
from typing import List, Optional



class JobItemPublic(JobItemBase):
    unit_price: float
    subtotal: float
    total_claimed: int
    remaining_on_hand: int
    service_name: str
    extra_service_name: str | None = None
    extra_service_price: float = 0.0
    
class JobItemCreate(JobItemBase):
    service_type_id: uuid.UUID
    extra_type_id: uuid.UUID | None = None
    
class PaymentPublic(PaymentBase):
    pass


class ClaimPublic(ClaimingHistoryBase):
    job_item_id: uuid.UUID
    
class ClaimCreate(ClaimingHistoryBase):
    job_item_id: str


class JobOrderPublic(JobOrderBase):
    id: uuid.UUID
    job_items: list[JobItemPublic] = Field(default_factory=list)
    payments: list[PaymentPublic] = Field(default_factory=list)
    claims: list[ClaimPublic] = Field(default_factory=list)
    payment_status: PaymentStatus
    total_due: float
    total_paid: float
    customer_name: str
    
class JobOrderCreate(JobOrderBase):
    customer_id: uuid.UUID | None = None
    customer_name: str | None = None
    customer_address: str | None = None
    customer_contact_no: str | None = None
    customer_email: str | None = None
    job_items: list["JobItemCreate"] = Field(default_factory=list)
    payments: Optional[List["PaymentPublic"]] = None
    claims: Optional[List["ClaimCreate"]] = None