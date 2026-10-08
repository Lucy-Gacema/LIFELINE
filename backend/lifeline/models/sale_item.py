from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from database import Base
from lifeline.models.types import GUID, new_uuid


class SaleItem(Base):
    __tablename__ = "sale_items"

    sale_item_id = Column(GUID(), primary_key=True, default=new_uuid)
    sale_id = Column(GUID(), ForeignKey("sales.sale_id"), nullable=False)
    product_id = Column(GUID(), ForeignKey("products.product_id"), nullable=True)

    product_name_snapshot = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    line_total = Column(Numeric(10, 2), nullable=False)

    quantity_refunded = Column(Integer, nullable=False, default=0)

    product = relationship("Product")

    @property
    def item_name(self) -> str | None:
        return self.product.product_name if self.product else self.product_name_snapshot
