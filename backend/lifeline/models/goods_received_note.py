from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base
from lifeline.models.types import GUID, new_uuid


class GoodsReceivedNote(Base):
    __tablename__ = "goods_received_notes"

    grn_id = Column(GUID(), primary_key=True, default=new_uuid)
    purchase_order_id = Column(
        GUID(), ForeignKey("purchase_orders.purchase_order_id"), nullable=False
    )
    received_by = Column(GUID(), ForeignKey("users.user_id"), nullable=True)
    received_at = Column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
    notes = Column(String, nullable=True)

    purchase_order = relationship("PurchaseOrder")
    items = relationship(
        "GoodsReceivedNoteItem", backref="grn", cascade="all, delete-orphan"
    )


class GoodsReceivedNoteItem(Base):
    __tablename__ = "goods_received_note_items"

    grn_item_id = Column(GUID(), primary_key=True, default=new_uuid)
    grn_id = Column(GUID(), ForeignKey("goods_received_notes.grn_id"), nullable=False)
    product_id = Column(GUID(), ForeignKey("products.product_id"), nullable=False)
    quantity_ordered = Column(Integer, nullable=False, default=0)
    quantity_received = Column(Integer, nullable=False)

    product = relationship("Product")

    @property
    def variance(self) -> int:
        return self.quantity_received - self.quantity_ordered
