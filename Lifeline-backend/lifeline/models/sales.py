import uuid
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional
from sqlalchemy.sql import func
from lifeline.schemas.sales import PaymentMethodEnum
from sqlalchemy import (
    Enum,
    Column,
    Integer,
    Numeric,
    ForeignKey,
    DateTime
)
from sqlalchemy.orm import relationship

from database import Base

class Sale(Base):
    __tablename__="sales"

    sale_id = Column(UUID(as_uuid=True), primary_key=True,default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id"), nullable=False, default=uuid.uuid4)
    quantity_sold = Column(Integer, nullable=False)
    total_amount = Column(Numeric(10,2), nullable=False)
    payment_method = Column(Enum(PaymentMethodEnum, native_enum = True), nullable=False, )
    timestamp = Column(DateTime, nullable=False, default=func.now(),server_default=func.now())

    product = relationship("Product", backref="sales")


    @property
    def item_name (self) ->Optional[str]:
        return self.product.product_name  if self.product else None
        



