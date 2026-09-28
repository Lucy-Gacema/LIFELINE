from sqlalchemy import Column, Numeric, String, ForeignKey, DateTime, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from lifeline.models.types import GUID, new_uuid


class Refund(Base):
    __tablename__ = "refunds"

    refund_id = Column(GUID(), primary_key=True, default=new_uuid)
    sale_id = Column(GUID(), ForeignKey("sales.sale_id"), nullable=False)
    processed_by = Column(GUID(), ForeignKey("users.user_id"), nullable=True)
    approved_by = Column(GUID(), ForeignKey("users.user_id"), nullable=True) 
    refund_method = Column(String, nullable=False, default="cash")
    total_amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())

    sale = relationship("Sale")
    items = relationship("RefundItem", backref="refund", cascade="all, delete-orphan")


class RefundItem(Base):
    __tablename__ = "refund_items"

    refund_item_id = Column(GUID(), primary_key=True, default=new_uuid)
    refund_id = Column(GUID(), ForeignKey("refunds.refund_id"), nullable=False)
    sale_item_id = Column(GUID(), ForeignKey("sale_items.sale_item_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    restocked = Column(Numeric(10, 2), nullable=False, default=1) 
