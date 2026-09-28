import enum
from sqlalchemy import Column, Numeric, String, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from lifeline.models.types import GUID, new_uuid


class ShiftStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"


class Shift(Base):
    __tablename__ = "shifts"

    shift_id = Column(GUID(), primary_key=True, default=new_uuid)
    cashier_id = Column(GUID(), ForeignKey("users.user_id"), nullable=False)
    status = Column(Enum(ShiftStatus, native_enum=False), nullable=False, default=ShiftStatus.OPEN)

    opening_cash = Column(Numeric(10, 2), nullable=False, default=0)
    opened_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())

    expected_cash = Column(Numeric(10, 2), nullable=True)
    actual_cash = Column(Numeric(10, 2), nullable=True)
    cash_difference = Column(Numeric(10, 2), nullable=True)
    closing_note = Column(String, nullable=True)
    closed_by_manager_id = Column(GUID(), ForeignKey("users.user_id"), nullable=True)
    closed_at = Column(DateTime, nullable=True)

    cashier = relationship("User", foreign_keys=[cashier_id])
