import uuid
from datetime import datetime
from decimal import Decimal

from sqlmodel import SQLModel

from app.enums import ReasonCategory, ReviewEntityType
from app.schemas.job_order import JobOrderPublic


class ForReviewPublic(SQLModel):
    id: uuid.UUID
    entity_type: ReviewEntityType
    entity_id: uuid.UUID
    entity_reference: str
    reason: str
    reason_category: ReasonCategory
    resolution_note: str | None
    created_at: datetime
    created_by_name: str
    resolved_at: datetime | None
    resolved_by_id: uuid.UUID | None
    resolved_by_name: str | None = None
    

class UnlinkedPaymentReviewData(SQLModel):
    id: uuid.UUID
    date_received: datetime
    reference_number: str | None
    amount: Decimal
    customer_name: str | None
    description: str | None
    account_id: uuid.UUID
    account_name: str | None
    
    
class ForReviewDetails(ForReviewPublic):
    entity: UnlinkedPaymentReviewData | JobOrderPublic