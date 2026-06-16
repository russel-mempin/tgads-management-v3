from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey
from datetime import datetime, timezone
import uuid
from pydantic import EmailStr
from app.enums import UserRoles, SizeUnit, PaymentMethod, PaymentStatus, JobStatus, ExpenseCategory
from app.utils.utils import compute_unit_price
from decimal import Decimal, ROUND_HALF_UP


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
    is_superAdmin: bool = Field(default=False)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    __tablename__ = "users"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    audit_logs: list["AuditLog"] = Relationship(back_populates="user")
    hashed_password: str = Field()


# ====================== CUSTOMERS =========================
class CustomerBase(SQLModel):
    name: str = Field()
    address: str = Field(default="N/A")
    contact_no: str = Field(default="N/A")
    email: str = Field(default="N/A")


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
    jo_number: int = Field(unique=True, index=True)
    date_received: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    override_payment_status: PaymentStatus | None = Field(default=None)
    is_active: bool = Field(default=True)
    payment_status: PaymentStatus = Field(default=PaymentStatus.UNPAID, index=True)
    overall_job_status: JobStatus = Field(default=JobStatus.FOR_LAYOUT, index=True)


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
    def computed_payment_status(self) -> PaymentStatus:
        if self.override_payment_status:
            return self.override_payment_status
        if self.total_paid <= 0:
            return PaymentStatus.UNPAID
        elif self.total_paid == self.total_due:
            return PaymentStatus.FULLY_PAID
        elif self.total_paid > self.total_due:
            return PaymentStatus.OVERCHARGED
        else:
            return PaymentStatus.PARTIAL

    @property
    def computed_overall_job_status(self) -> JobStatus:
        if not self.job_items:
            return JobStatus.FOR_LAYOUT

        priorities = {
            JobStatus.CANCELLED: 0,
            JobStatus.RELEASED: 1,
            JobStatus.FOR_PICKUP: 2,
            JobStatus.FOR_PRINTING: 3,
            JobStatus.FOR_APPROVAL: 4,
            JobStatus.FOR_LAYOUT: 5,
        }
        return max(self.job_items, key=lambda item: priorities.get(item.job_status, -1)).job_status

    def sync_computed_fields(self):
        self.payment_status = self.computed_payment_status
        self.overall_job_status = self.computed_overall_job_status

    @property
    def customer_name(self) -> str:
        return self.customer.name

    @property
    def customer_email(self) -> str:
        return self.customer.email

    @property
    def customer_contact_no(self) -> str:
        return self.customer.contact_no
    
    
# ====================== JOB ITEMS =========================
class JobItemBase(SQLModel):
    jo_number: int = Field()
    item_id: str = Field(unique=True, index=True)
    description: str | None = Field(default=None)
    height: float = Field(default=0.0)
    width: float = Field(default=0.0)
    size_unit: SizeUnit
    quantity: int = Field(default=0)
    job_status: JobStatus
    due_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    discount: float = Field(default=0.0)
    extra_charge: float = Field(default=0.0)
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
        price = compute_unit_price(self.height, self.width, self.service_type, self.size_unit)
        return float(Decimal(str(price)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

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
        extra_type_price = self.extra_type.price if self.extra_type else 0.0
        return ((self.unit_price + self.extra_charge) * self.quantity) + extra_type_price - self.discount
    
    
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



# ====================== EXPENSES =========================
class ExpenseBase(SQLModel):
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    category: ExpenseCategory
    amount: float = Field()
    description: str = Field()
    
class Expense(ExpenseBase, table=True):
    __tablename__ = "expenses"  # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    

# ====================== MISC SALES =========================
class MiscSaleBase(SQLModel):
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = Field()
    amount: float = Field()
    
class MiscSale(MiscSaleBase, table=True):
    __tablename__ = "misc_sales" # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    
# ====================== CASH ANCHOR =========================
class CashAnchor(SQLModel, table=True):
    __tablename__ = "cash_anchor" # type: ignore
    id: int = Field(default=1, primary_key=True)
    year: int = Field()
    month: int = Field()
    beginning_balance: float = Field()