from enum import Enum

class SizeUnit(str, Enum):
    INCHES = "in."
    FEET = "ft."
    CENTIMETER = "cm."
    MILLIMETER = "mm."
    NA = "N/A"
    
    
class UserRoles(str, Enum):
    ADMIN = "Admin"
    USER = "User"
    OWNER = "Owner"
    
    
class PaymentStatus(str, Enum):
    UNPAID = "Unpaid"
    PARTIAL = "Partial"
    FULLY_PAID = "Fully Paid"
    CREDIT = "Credit"
    REFUNDED = "Refunded"
    OVERCHARGED = "Overcharged"
    
    
class JobStatus(str, Enum):
    PENDING = "Pending"
    FOR_LAYOUT = "For Layout"
    FOR_APPROVAL = "For Approval"
    FOR_PRINTING = "For Printing"
    FOR_PICKUP = "For Pickup"
    RELEASED = "Released"
    CANCELLED = "Cancelled"
    
    
class TransactionSource(str, Enum):
    PAYMENT = "payment"
    EXPENSE = "expense"
    MISC_SALE = "misc_sale"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"
    EXPENSE_REVERSAL = "expense_reversal"
    
class ExpenseCategory(str, Enum):
    FOOD = "Food"
    MAINTENANCE = "Maintenance"
    UTILITIES = "Utilities"
    TRANSPORTATION = "Transportation"
    SUPPLIES = "Supplies"
    PAYROLL = "Payroll"
    BENEFITS = "Benefits"
    PRODUCTION = "Production"
    MISCELLANEOUS = "Miscellaneous"
    
class AccountType(str, Enum):
    CASH_ON_HAND = "Cash"
    BANK = "Bank"
    EWALLET = "E-Wallet"