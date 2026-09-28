import enum
from typing import Optional
from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from lifeline.models.types import GUID, new_uuid


class SaleStatus(str, enum.Enum):
    COMPLETED = "completed"
    HELD = "held"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class Sale(Base):
    __tablename__ = "sales"

    sale_id = Column(GUID(), primary_key=True, default=new_uuid)
    idempotency_key = Column(String, nullable=False, unique=True, index=True)
    receipt_number = Column(String, nullable=True, unique=True, index=True)

    customer_id = Column(GUID(), ForeignKey("customers.customer_id"), nullable=True)
    cashier_id = Column(GUID(), ForeignKey("users.user_id"), nullable=True)
    shift_id = Column(GUID(), ForeignKey("shifts.shift_id"), nullable=True)

    subtotal = Column(Numeric(10, 2), nullable=False, default=0)
    discount_total = Column(Numeric(10, 2), nullable=False, default=0)
    tax_total = Column(Numeric(10, 2), nullable=False, default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)

    status = Column(Enum(SaleStatus, native_enum=False), nullable=False, default=SaleStatus.COMPLETED)
    note = Column(String, nullable=True)
    created_via = Column(String, nullable=False, default="manual") 

    timestamp = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())


    synced = Column(Boolean, nullable=False, default=True)
    device_id = Column(String, nullable=True)

    customer = relationship("Customer", backref="sales")
    cashier = relationship("User")
    items = relationship("SaleItem", backref="sale", cascade="all, delete-orphan")
    payments = relationship("Payment", backref="sale", cascade="all, delete-orphan")

    @property
    def item_count(self) -> int:
        return sum(i.quantity for i in self.items)
