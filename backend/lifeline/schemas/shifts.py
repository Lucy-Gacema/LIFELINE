import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ShiftOpen(BaseModel):
    opening_cash: Decimal = 0


class ShiftClose(BaseModel):
    actual_cash: Decimal
    closing_note: Optional[str] = None


class CashMovementCreate(BaseModel):
    type: str  
    amount: Decimal
    reason: Optional[str] = None


class ShiftOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    shift_id: uuid.UUID
    cashier_id: uuid.UUID
    status: str
    opening_cash: Decimal
    opened_at: datetime
    expected_cash: Optional[Decimal] = None
    actual_cash: Optional[Decimal] = None
    cash_difference: Optional[Decimal] = None
    closed_at: Optional[datetime] = None
