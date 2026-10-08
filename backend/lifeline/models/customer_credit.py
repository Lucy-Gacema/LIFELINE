import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base
from lifeline.models.types import GUID, new_uuid


class CreditTransactionType(str, enum.Enum):
    CHARGE = "charge"
    PAYMENT = "payment"
    DEPOSIT = "deposit"
    REFUND_CREDIT = "refund_credit"


class CustomerCredit(Base):
    __tablename__ = "customer_credit_transactions"

    transaction_id = Column(GUID(), primary_key=True, default=new_uuid)
    customer_id = Column(GUID(), ForeignKey("customers.customer_id"), nullable=False)
    sale_id = Column(GUID(), ForeignKey("sales.sale_id"), nullable=True)
    type = Column(Enum(CreditTransactionType, native_enum=False), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    balance_after = Column(Numeric(10, 2), nullable=False)
    note = Column(String, nullable=True)
    created_by = Column(GUID(), ForeignKey("users.user_id"), nullable=True)
    created_at = Column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )

    customer = relationship("Customer", backref="credit_transactions")
