import uuid
from datetime import datetime
from sqlmodel import SQLModel


class ForReviewPublic(SQLModel):
    id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    entity_reference: str
    reason: str
    reason_category: str
    created_at: datetime
    created_by_name: str
    resolved_at: datetime | None
    resolved_by_id: uuid.UUID | None
    resolved_by_name: str | None = None