import enum
from sqlalchemy import Column, Numeric, String, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.sql import func
from database import Base
from lifeline.models.types import GUID, new_uuid


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    MPESA = "mpesa"
    QR = "qr"
    WALLET = "wallet"
    STORE_CREDIT = "store_credit"
    CUSTOM = "custom"


class PaymentVerificationStatus(str, enum.Enum):
    VERIFIED = "verified"             
    MANUALLY_RECORDED = "manually_recorded"  
    FAILED = "failed"
    PENDING = "pending"


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(GUID(), primary_key=True, default=new_uuid)
    sale_id = Column(GUID(), ForeignKey("sales.sale_id"), nullable=False)
    method = Column(Enum(PaymentMethod, native_enum=False), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    amount_tendered = Column(Numeric(10, 2), nullable=True)  
    change_given = Column(Numeric(10, 2), nullable=True)

    verification_status = Column(
        Enum(PaymentVerificationStatus, native_enum=False),
        nullable=False,
        default=PaymentVerificationStatus.MANUALLY_RECORDED,
    )
    transaction_reference = Column(String, nullable=True)  
    phone_number = Column(String, nullable=True)

    cashier_id = Column(GUID(), ForeignKey("users.user_id"), nullable=True)
    timestamp = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
