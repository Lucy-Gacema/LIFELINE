import uuid
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    customer_id: uuid.UUID
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    loyalty_points: Decimal
    store_credit_balance: Decimal
    outstanding_balance: Decimal
    notes: Optional[str] = None
