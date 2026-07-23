import uuid
from datetime import datetime
from sqlmodel import SQLModel


class ForReviewPublic(SQLModel):
    id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    entity_reference: str
    reason: str
    created_at: datetime
    resolved_at: datetime
    resolved_by_id: uuid.UUID | None
    resolved_by_name: str | None = None