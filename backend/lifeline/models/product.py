from sqlalchemy import Column, Integer, Numeric, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from database import Base
from lifeline.models.types import GUID, new_uuid


class Product(Base):
    __tablename__ = "products"

    product_id = Column(GUID(), primary_key=True, default=new_uuid)
    product_name = Column(String, nullable=False, index=True)
    sku = Column(String, nullable=True, unique=True, index=True)
    barcode = Column(String, nullable=True, unique=True, index=True)
    category_id = Column(GUID(), ForeignKey("categories.category_id"), nullable=True)
    unit = Column(String, nullable=False, default="pc")  
    buying_price = Column(Numeric(10, 2), nullable=True, default=0)
    selling_price = Column(Numeric(10, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), nullable=False, default=0)
    current_stock = Column(Integer, nullable=False, default=0)
    minimum_stock = Column(Integer, nullable=False, default=0)
    maximum_stock = Column(Integer, nullable=True)
    supplier_id = Column(GUID(), ForeignKey("suppliers.supplier_id"), nullable=True)
    image_url = Column(String, nullable=True)
    aliases = Column(JSON, nullable=True, default=list) 
    is_favorite = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)

    category = relationship("Category", backref="products")
    supplier = relationship("Supplier", backref="products")

    @property
    def stock_status(self) -> str:
        if self.current_stock <= 0:
            return "out_of_stock"
        if self.current_stock <= self.minimum_stock:
            return "critical" if self.current_stock <= max(self.minimum_stock // 2, 1) else "low"
        return "healthy"
