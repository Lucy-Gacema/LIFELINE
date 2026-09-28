import enum
from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from lifeline.models.types import GUID, new_uuid


class PurchaseOrderStatus(str, enum.Enum):
    DRAFT = "draft"
    ORDERED = "ordered"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    purchase_order_id = Column(GUID(), primary_key=True, default=new_uuid)
    supplier_id = Column(GUID(), ForeignKey("suppliers.supplier_id"), nullable=False)
    status = Column(Enum(PurchaseOrderStatus, native_enum=False), nullable=False, default=PurchaseOrderStatus.DRAFT)
    created_by = Column(GUID(), ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    notes = Column(String, nullable=True)

    supplier = relationship("Supplier", backref="purchase_orders")
    items = relationship("PurchaseOrderItem", backref="purchase_order", cascade="all, delete-orphan")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    purchase_order_item_id = Column(GUID(), primary_key=True, default=new_uuid)
    purchase_order_id = Column(GUID(), ForeignKey("purchase_orders.purchase_order_id"), nullable=False)
    product_id = Column(GUID(), ForeignKey("products.product_id"), nullable=False)
    quantity_ordered = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=False)

    product = relationship("Product")
