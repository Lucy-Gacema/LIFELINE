import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    category: str = Field(..., min_length=1)
    amount: Decimal = Field(..., gt=0)
    payment_method: str = "cash"
    note: str | None = None
    receipt_url: str | None = None


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    expense_id: uuid.UUID
    category: str
    amount: Decimal
    payment_method: str
    note: str | None = None
    date: datetime
