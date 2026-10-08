from sqlalchemy import Column, Numeric, String

from database import Base
from lifeline.models.types import GUID, new_uuid


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(GUID(), primary_key=True, default=new_uuid)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    amount_owed = Column(Numeric(10, 2), nullable=False, default=0)
    notes = Column(String, nullable=True)
