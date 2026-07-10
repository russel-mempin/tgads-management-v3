from app.models import ServiceBase, ExtraService
import uuid
from sqlmodel import SQLModel
from app.enums import SizeUnit


class ServicePublic(ServiceBase):
    id: uuid.UUID
    
class ServiceCreate(ServiceBase):
    pass

class ExtraPublic(SQLModel):
    id: uuid.UUID
    name: str
    price: float

class ExtraCreate(SQLModel):
    name: str
    price: float

class ServiceUpdate(SQLModel):
    name: str | None = None
    abbreviation: str | None = None
    price: float | None = None
    unit: str | None = None
    is_area_based: bool | None = None
    required_measurement_unit: SizeUnit | None = None