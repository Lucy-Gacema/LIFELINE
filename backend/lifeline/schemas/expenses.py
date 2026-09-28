import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ExpenseCreate(BaseModel):
    category: str
    amount: Decimal
    payment_method: str = "cash"
    note: Optional[str] = None
    receipt_url: Optional[str] = None


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    expense_id: uuid.UUID
    category: str
    amount: Decimal
    payment_method: str
    note: Optional[str] = None
    date: datetime
