import uuid

from sqlmodel import Field, SQLModel

from app.enums import SizeUnit
from app.models import ServiceBase


class ServicePriceTierPublic(SQLModel):
    min_threshold: float
    max_threshold: float | None
    rate: float


class ServiceOptionPublic(SQLModel):
    id: uuid.UUID
    service_id: uuid.UUID
    name: str
    base_rate: float
    is_active: bool
    minimum_consumption: float | None
    stock_increment: float | None
    full_service_name: str
    is_priced: bool
    price_tiers: list[ServicePriceTierPublic] = Field(default_factory=list)


class ServicePublic(ServiceBase):
    id: uuid.UUID
    options: list[ServiceOptionPublic] = Field(default_factory=list)


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