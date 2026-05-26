from app.models import ServiceTypeBase
import uuid
from sqlmodel import SQLModel
from app.enums import SizeUnit


class ServicePublic(ServiceTypeBase):
    id: uuid.UUID
    
class ServiceCreate(ServiceTypeBase):
    pass

class ServiceUpdate(SQLModel):
    name: str | None = None
    abbreviation: str | None = None
    price: float | None = None
    unit: str | None = None
    is_area_based: bool | None = None
    required_measurement_unit: SizeUnit | None = None