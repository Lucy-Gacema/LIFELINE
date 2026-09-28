from sqlalchemy import Column, Numeric, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base
from lifeline.models.types import GUID, new_uuid


class Expense(Base):
    __tablename__ = "expenses"

    expense_id = Column(GUID(), primary_key=True, default=new_uuid)
    category = Column(String, nullable=False)  
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String, nullable=False, default="cash")
    note = Column(String, nullable=True)
    receipt_url = Column(String, nullable=True)
    created_by = Column(GUID(), ForeignKey("users.user_id"), nullable=True)
    date = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
