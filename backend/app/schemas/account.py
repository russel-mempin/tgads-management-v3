from sqlmodel import SQLModel
import uuid

class AccountOption(SQLModel):
    id: uuid.UUID
    name: str