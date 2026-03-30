from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey
from datetime import datetime, timezone
import uuid
from enum import Enum
from pydantic import EmailStr


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
class UserRoles(str, Enum):
    ADMIN = "Admin"
    USER = "User"


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
    name: str = Field()
    price: float = Field(default=0.0)
    unit: str = Field()


class ServiceType(ServiceTypeBase, table=True):
    __tablename__ = "service_types"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    job_items: list["JobItem"] = Relationship(back_populates="service_type")


# ====================== EXTRA TYPES =========================
class ExtraType(SQLModel, table=True):
    __tablename__ = "extra_types"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field()
    price: float = Field(default=0.0)

    job_items: list["JobItem"] = Relationship(back_populates="extra_type")


# ====================== JOB ORDERS =========================
class JobOrderBase(SQLModel):
    jo_number: str = Field()
    date_received: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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


# ====================== JOB ITEMS =========================
class SizeUnit(str, Enum):
    INCHES = "in."
    FEET = "ft."
    CENTIMETER = "cm."


class JobStatus(str, Enum):
    FOR_LAYOUT = "For Layout"
    FOR_APPROVAL = "For Approval"
    FOR_PRINTING = "For Printing"
    FOR_PICKUP = "For Pickup"
    RELEASED = "Released"
    CANCELLED = "Cancelled"


class PaymentStatus(str, Enum):
    UNPAID = "Unpaid"
    PARTIAL = "Partial"
    FULLY_PAID = "Fully Paid"
    CREDIT = "Credit"
    REFUNDED = "Refunded"


class PaperSize(str, Enum):
    SHORT = "Short"
    LONG = "Long"
    A4 = "A4"
    A3 = "A3"


class JobItemBase(SQLModel):
    description: str = Field()
    height: float = Field(default=0.0)
    width: float = Field(default=0.0)
    size_unit: SizeUnit
    paper_size: PaperSize
    unit_price: float = Field(default=0.0)
    quantity: int = Field(default=0)
    subtotal: float = Field(default=0.0)
    job_status: JobStatus
    payment_status: PaymentStatus
    due_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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


# ====================== PAYMENTS =========================
class PaymentMethod(str, Enum):
    CASH = "Cash"
    GCASH = "GCash"
    CHEQUE = "Cheque"


class Payment(SQLModel, table=True):
    __tablename__ = "payments"  # type: ignore
    date_received: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    method: PaymentMethod
    amount: float = Field(default=0.0)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_order_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("job_orders.id", ondelete="CASCADE"), nullable=False
        )
    )

    job_order: "JobOrder" = Relationship(back_populates="payments")


# ====================== CLAIMING HISTORY =========================
class ClaimingHistory(SQLModel, table=True):
    __tablename__ = "claiming_history"  # type: ignore
    date_claimed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    name: str = Field()
    pcs_claimed: int = Field(default=0)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_order_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("job_orders.id", ondelete="CASCADE"), nullable=False
        )
    )

    job_order: "JobOrder" = Relationship(back_populates="claims")
