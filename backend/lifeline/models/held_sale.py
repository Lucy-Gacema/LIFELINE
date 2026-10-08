from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.sql import func

from database import Base
from lifeline.models.types import GUID, new_uuid


class HeldSale(Base):
    __tablename__ = "held_sales"

    held_sale_id = Column(GUID(), primary_key=True, default=new_uuid)
    label = Column(String, nullable=True)
    cart_snapshot = Column(JSON, nullable=False)
    created_by = Column(GUID(), ForeignKey("users.user_id"), nullable=True)
    created_at = Column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
