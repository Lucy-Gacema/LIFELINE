import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.sql import func

from database import Base
from lifeline.models.types import GUID, new_uuid


class CashMovementType(str, enum.Enum):
    SALE = "sale"
    DROP = "drop"
    PAYOUT = "payout"
    ADJUSTMENT = "adjustment"


class CashMovement(Base):
    __tablename__ = "cash_movements"

    cash_movement_id = Column(GUID(), primary_key=True, default=new_uuid)
    shift_id = Column(GUID(), ForeignKey("shifts.shift_id"), nullable=False)
    type = Column(Enum(CashMovementType, native_enum=False), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(String, nullable=True)
    created_by = Column(GUID(), ForeignKey("users.user_id"), nullable=True)
    timestamp = Column(
        DateTime, nullable=False, default=func.now(), server_default=func.now()
    )
