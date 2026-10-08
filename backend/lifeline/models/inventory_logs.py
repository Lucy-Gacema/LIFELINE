from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base
from lifeline.models.types import GUID, new_uuid
from lifeline.schemas.inventory_logs import ReasonEnum


class InventoryLogs(Base):
    __tablename__ = "inventory_logs"

    inventory_logs_id = Column(GUID(), primary_key=True, default=new_uuid)
    product_id = Column(GUID(), ForeignKey("products.product_id"), nullable=False)
    quantity_changed = Column(Integer, nullable=False)
    previous_quantity = Column(Integer, nullable=False, default=0)
    new_quantity = Column(Integer, nullable=False, default=0)
    reason = Column(Enum(ReasonEnum, native_enum=False), nullable=False)
    note = Column(String, nullable=True)
    created_by = Column(GUID(), ForeignKey("users.user_id"), nullable=True)
    timestamp = Column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )

    product = relationship("Product", backref="inventory_logs")

    @property
    def product_name(self) -> str | None:
        return self.product.product_name if self.product else None
