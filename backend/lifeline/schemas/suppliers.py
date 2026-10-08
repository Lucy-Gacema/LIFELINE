import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SupplierCreate(BaseModel):
    name: str
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    notes: str | None = None


class SupplierOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    supplier_id: uuid.UUID
    name: str
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    amount_owed: Decimal
    notes: str | None = None
