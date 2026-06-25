from sqlmodel import SQLModel
import uuid
from datetime import datetime


class AuditLogPublic(SQLModel):
    id: uuid.UUID
    action: str
    user_id: uuid.UUID | None
    user_name: str | None
    timestamp: datetime