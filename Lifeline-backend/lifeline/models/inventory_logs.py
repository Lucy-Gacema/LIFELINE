import uuid
from lifeline.schemas.inventory_logs import ReasonEnum
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional
from sqlalchemy.sql import func
from sqlalchemy import (
    Enum,
    Column,
    Integer,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from database import Base

class InventoryLogs(Base):
    __tablename__ = "inventory_logs"

    inventory_logs_id = Column(UUID(as_uuid=True), primary_key=True, default= uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id"), nullable=False, default=uuid.uuid4)
    quantity_changed = Column(Integer, nullable=False)
    reason = Column (Enum(ReasonEnum, native_enum = True), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())

    product = relationship("Product", backref="inventory_logs")


    @property
    def product_name(self) ->Optional[str]:
        return self.product.product_name if self.product else None
    