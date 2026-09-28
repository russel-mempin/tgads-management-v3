import uuid

from sqlmodel import SQLModel

from app.models import ExtraServiceBase


class ExtraPublic(ExtraServiceBase):
    id: uuid.UUID


class ExtraCreate(ExtraServiceBase):
    pass


class ExtraUpdate(SQLModel):
    name: str | None = None
    price: float | None = None
    is_active: bool | None = None