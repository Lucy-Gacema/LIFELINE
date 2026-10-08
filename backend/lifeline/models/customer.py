from sqlalchemy import Column, Numeric, String

from database import Base
from lifeline.models.types import GUID, new_uuid


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(GUID(), primary_key=True, default=new_uuid)
    name = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=True, index=True)
    email = Column(String, nullable=True)
    loyalty_points = Column(Numeric(10, 2), nullable=False, default=0)
    store_credit_balance = Column(Numeric(10, 2), nullable=False, default=0)
    outstanding_balance = Column(Numeric(10, 2), nullable=False, default=0)
    notes = Column(String, nullable=True)
