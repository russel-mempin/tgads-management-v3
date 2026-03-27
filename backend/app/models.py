from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone, date
import uuid
from enum import Enum
from pydantic import EmailStr

# ====================== AUDIT LOGS =========================
class AuditLog(SQLModel, table=True): 
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    action: str
    performed_by: uuid.UUID | None = Field(default=None, foreign_key="users.id")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))    
    
    
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
    __tablename__ = "users" # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field()
    
    
# ====================== CUSTOMERS =========================
class CustomerBase(SQLModel):
    name: str = Field()
    address: str = Field()
    contact_no: str = Field()
    email: str = Field()
        

class Customer(CustomerBase, table=True):
    __tablename__ = "customers" # type: ignore
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    job_orders: list["JobOrder"] = Relationship(back_populates="customer")
    
    
# ====================== SERVICE TYPES =========================
class ServiceTypeBase(SQLModel):
    name: str = Field()
    price: float = Field(default=0.0)
    unit: str = Field()    

    
class ServiceType(ServiceTypeBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    

# ====================== EXTRA TYPES =========================
class ExtraTypeBase(SQLModel):
    name: str = Field()
    price: float = Field(default=0.0)

    
class ExtraType(ExtraTypeBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    
# ====================== JOB ORDERS =========================
class JobOrderBase(SQLModel):
    jo_number: str = Field()
    date_received: date = Field()

        
class JobOrder(JobOrderBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    customer_id: uuid.UUID = Field(foreign_key="customers.id")
    
    customer: "Customer" = Relationship(back_populates="job_orders")
    

# ====================== JOB ITEMS =========================
