import uuid
from datetime import datetime
from sqlmodel import SQLModel


class VoidJobOrderPublic(SQLModel):
    id: uuid.UUID
    jo_number: int
    job_date: datetime
    voided_at: datetime
    reason: str
    voided_by_name: str 