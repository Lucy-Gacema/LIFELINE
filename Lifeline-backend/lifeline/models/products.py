import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String
)

from database import Base

class Product(Base):
    __tablename__="products"
    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_name = Column(String, nullable=False)
    buying_price = Column(Numeric(10,2), nullable=False)
    selling_price = Column(Numeric(10,2), nullable=False)
    current_stock = Column(Integer, nullable=False)


 


    