from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey
from datetime import datetime, timezone
import uuid
from pydantic import EmailStr
from app.enums import UserRoles, SizeUnit, PaymentMethod, PaymentStatus, JobStatus, PaperSize
from app.utils.utils import compute_unit_price


# ====================== AUDIT LOGS =========================
class AuditLog(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    action: str
    user_id: uuid.UUID | None = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: "User" = Relationship(back_populates="audit_logs")


# ====================== USERS =========================
class UserBase(SQLModel):
    first_name: str = Field()
    last_name: str = Field()
    username: str = Field(unique=True, index=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    role: UserRoles
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    __tablename__ = "users"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    audit_logs: list["AuditLog"] = Relationship(back_populates="user")
    hashed_password: str = Field()


# ====================== CUSTOMERS =========================
class CustomerBase(SQLModel):
    name: str = Field()
    address: str = Field()
    contact_no: str = Field()
    email: str = Field()


class Customer(CustomerBase, table=True):
    __tablename__ = "customers"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    job_orders: list["JobOrder"] = Relationship(
        back_populates="customer",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# ====================== SERVICE TYPES =========================
class ServiceTypeBase(SQLModel):
    name: str = Field(unique=True, index=True)
    abbreviation: str = Field(unique=True, index=True)
    price: float = Field(default=0.0)
    unit: str = Field()
    is_area_based: bool = Field(default=True)
    required_measurement_unit: SizeUnit
    is_active: bool = Field(default=True)


class ServiceType(ServiceTypeBase, table=True):
    __tablename__ = "service_types"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    job_items: list["JobItem"] = Relationship(back_populates="service_type")


# ====================== EXTRA TYPES =========================
class ExtraType(SQLModel, table=True):
    __tablename__ = "extra_types"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    price: float = Field(default=0.0)
    is_active: bool = Field(default=True)

    job_items: list["JobItem"] = Relationship(back_populates="extra_type")


# ====================== JOB ORDERS =========================
class JobOrderBase(SQLModel):
    jo_number: str = Field()
    date_received: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    override_payment_status: PaymentStatus | None = Field(default=None)
    is_active: bool = Field(default=True)

class JobOrder(JobOrderBase, table=True):
    __tablename__ = "job_orders"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    customer_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    )

    customer: "Customer" = Relationship(back_populates="job_orders")
    job_items: list["JobItem"] = Relationship(
        back_populates="job_order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    payments: list["Payment"] = Relationship(
        back_populates="job_order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    claims: list["ClaimingHistory"] = Relationship(
        back_populates="job_order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    
    @property
    def total_due(self) -> float:
        return sum(item.subtotal for item in self.job_items)

    @property
    def total_paid(self) -> float:
        return sum(p.amount for p in self.payments)

    @property
    def payment_status(self) -> PaymentStatus:
        if self.total_paid <= 0:
            return PaymentStatus.UNPAID
        elif self.total_paid >= self.total_due:
            return PaymentStatus.FULLY_PAID
        else:
            return PaymentStatus.PARTIAL
        
    @property
    def customer_name(self) -> str:
        return self.customer.name


# ====================== JOB ITEMS =========================
class JobItemBase(SQLModel):
    jo_number: str = Field()
    item_id: str = Field(unique=True, index=True)
    description: str | None = Field(default=None)
    height: float = Field(default=0.0)
    width: float = Field(default=0.0)
    size_unit: SizeUnit
    paper_size: PaperSize
    quantity: int = Field(default=0)
    job_status: JobStatus
    due_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    discount: float = Field(default=0.0)
    notes: str | None = Field(default=None)


class JobItem(JobItemBase, table=True):
    __tablename__ = "job_items"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    job_order_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("job_orders.id", ondelete="CASCADE"), nullable=False
        )
    )
    service_type_id: uuid.UUID = Field(foreign_key="service_types.id")
    extra_type_id: uuid.UUID | None = Field(default=None, foreign_key="extra_types.id")

    job_order: "JobOrder" = Relationship(back_populates="job_items")
    service_type: "ServiceType" = Relationship(back_populates="job_items")
    extra_type: "ExtraType" = Relationship(back_populates="job_items")
    claims: list["ClaimingHistory"] = Relationship(back_populates="job_item")


    @property
    def unit_price(self) -> float:
        return compute_unit_price(self.height, self.width, self.service_type)

    @property
    def total_claimed(self) -> int:
        return sum(c.pcs_claimed for c in self.claims)

    @property
    def remaining_on_hand(self) -> int:
        return self.quantity - self.total_claimed
    
    @property
    def service_name(self) -> str:
        return self.service_type.name
    
    @property
    def extra_service_name(self) -> str | None:
        return self.extra_type.name if self.extra_type else None
    
    @property
    def extra_service_price(self) -> float:
        return self.extra_type.price if self.extra_type else 0.0
    
    @property
    def subtotal(self) -> float:
        extra = self.extra_type.price if self.extra_type else 0.0
        return (self.unit_price * self.quantity) + extra - self.discount
    
    
# ====================== PAYMENTS =========================
class PaymentBase(SQLModel):
    date_received: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    method: PaymentMethod
    amount: float = Field(default=0.0)    
    

class Payment(PaymentBase, table=True):
    __tablename__ = "payments"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_order_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("job_orders.id", ondelete="CASCADE"), nullable=False
        )
    )

    job_order: "JobOrder" = Relationship(back_populates="payments")


# ====================== CLAIMING HISTORY =========================
class ClaimingHistoryBase(SQLModel):
    date_claimed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    name: str = Field()
    pcs_claimed: int = Field(default=0)
    claimed_item_id: str = Field()
    
    
class ClaimingHistory(ClaimingHistoryBase, table=True):
    __tablename__ = "claiming_history"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_order_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("job_orders.id", ondelete="CASCADE"), nullable=False
        )
    )
    job_item_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("job_items.id", ondelete="CASCADE"), nullable=False
        )
    )

    job_order: "JobOrder" = Relationship(back_populates="claims")
    job_item: "JobItem" = Relationship(back_populates="claims")
