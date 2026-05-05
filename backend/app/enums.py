from enum import Enum

class SizeUnit(str, Enum):
    INCHES = "in."
    FEET = "ft."
    CENTIMETER = "cm."
    
class UserRoles(str, Enum):
    ADMIN = "Admin"
    USER = "User"
    
class PaymentStatus(str, Enum):
    UNPAID = "Unpaid"
    PARTIAL = "Partial"
    FULLY_PAID = "Fully Paid"
    CREDIT = "Credit"
    REFUNDED = "Refunded"
    
class JobStatus(str, Enum):
    FOR_LAYOUT = "For Layout"
    FOR_APPROVAL = "For Approval"
    FOR_PRINTING = "For Printing"
    FOR_PICKUP = "For Pickup"
    RELEASED = "Released"
    CANCELLED = "Cancelled"

class PaperSize(str, Enum):
    SHORT = "Short"
    LONG = "Long"
    A4 = "A4"
    A3 = "A3"
    NOT_APPLICABLE = "N/A"
    
class PaymentMethod(str, Enum):
    CASH = "Cash"
    GCASH = "GCash"
    CHEQUE = "Cheque"