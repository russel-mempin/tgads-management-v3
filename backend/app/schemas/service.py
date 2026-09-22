import uuid
from decimal import Decimal

from sqlmodel import Field, SQLModel

from app.enums import SizeUnit
from app.models import ServiceBase, ServicePriceTierBase


class ServicePriceTierPublic(ServicePriceTierBase):
    id: uuid.UUID


class ServiceOptionPublic(SQLModel):
    id: uuid.UUID
    service_id: uuid.UUID
    name: str
    base_rate: float
    is_active: bool
    minimum_consumption: float | None = None
    stock_increment: float | None = None
    full_service_name: str
    is_priced: bool
    price_tiers: list[ServicePriceTierPublic] = Field(default_factory=list)


class ServicePublic(ServiceBase):
    id: uuid.UUID
    options: list[ServiceOptionPublic] = Field(default_factory=list)


class ServiceOptionCreate(SQLModel):
    name: str
    base_rate: Decimal
    minimum_consumption: float | None = None
    stock_increment: float | None = None
    price_tiers: list[ServicePriceTierBase] | None = None 


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