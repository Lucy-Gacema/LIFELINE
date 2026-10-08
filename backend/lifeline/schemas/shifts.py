import enum
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ShiftOpen(BaseModel):
    opening_cash: Decimal = Field(0, ge=0)


class ShiftClose(BaseModel):
    actual_cash: Decimal = Field(..., ge=0)
    closing_note: str | None = None


class CashMovementType(str, enum.Enum):
    DROP = "drop"
    PAYOUT = "payout"
    ADJUSTMENT = "adjustment"


class CashMovementCreate(BaseModel):
    type: CashMovementType
    amount: Decimal
    reason: str | None = None


class ShiftOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    shift_id: uuid.UUID
    cashier_id: uuid.UUID
    status: str
    opening_cash: Decimal
    opened_at: datetime
    expected_cash: Decimal | None = None
    actual_cash: Decimal | None = None
    cash_difference: Decimal | None = None
    closed_at: datetime | None = None
