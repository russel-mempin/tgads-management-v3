# mga irereturn pag nag read sa job orders
# jo number, customer name, service type, size, deadline, job status, overall payment status,
# jo number, customer name, overall payment galing sa job_orders table
# service_type, size, deadline, job_status galing sa job_items
# payments kasama rin dapat
# claim history kasama rin
from app.models import JobItemBase, PaymentBase, ClaimingHistoryBase, JobOrderBase, PaymentStatus
from sqlmodel import Field
import uuid


class JobItemPublic(JobItemBase):
    unit_price: float
    subtotal: float
    total_claimed: int
    remaining_on_hand: int
    service_name: str
    extra_service_name: str
    extra_service_price: float
    
    
class PaymentPublic(PaymentBase):
    pass


class ClaimPublic(ClaimingHistoryBase):
    pass


class JobOrderPublic(JobOrderBase):
    id: uuid.UUID
    job_items: list[JobItemPublic] = Field(default_factory=list)
    payments: list[PaymentPublic] = Field(default_factory=list)
    claims: list[ClaimPublic] = Field(default_factory=list)
    payment_status: PaymentStatus
    total_due: float
    total_paid: float
    customer_name: str