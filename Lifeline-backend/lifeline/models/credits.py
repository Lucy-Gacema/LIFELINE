import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Column,
    Numeric,
    String,
    ForeignKey,
    Boolean,
    DateTime
)
from sqlalchemy.orm import relationship

from database import Base

class Credit(Base):
    __tablename__ = "credits"

    credit_id = Column(UUID(as_uuid = True), primary_key=True, default=uuid.uuid4)
    sale_id = Column(UUID(as_uuid=True), ForeignKey('sales.sale_id'), nullable=False, default=uuid.uuid4)
    customer_name = Column(String, nullable=False) 
    amount_owed = Column(Numeric(5,2), nullable=False)
    is_paid = Column(Boolean, nullable=False, default=False)
    date_borrowed = Column(DateTime, nullable=False)

    sale = relationship("Sale", backref="credits")

    

