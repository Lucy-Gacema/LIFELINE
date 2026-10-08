import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1)
    phone: str | None = None
    email: str | None = None
    notes: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    notes: str | None = None


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    customer_id: uuid.UUID
    name: str
    phone: str | None = None
    email: str | None = None
    loyalty_points: Decimal
    store_credit_balance: Decimal
    outstanding_balance: Decimal
    notes: str | None = None
