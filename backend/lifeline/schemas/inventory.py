import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from lifeline.schemas.inventory_logs import ReasonEnum


class InventoryAdjustment(BaseModel):
    product_id: uuid.UUID
    quantity_changed: int
    reason: ReasonEnum
    note: str | None = None
    allow_negative_stock: bool = False


class InventoryLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    inventory_logs_id: uuid.UUID
    product_id: uuid.UUID
    product_name: str | None = None
    quantity_changed: int
    previous_quantity: int
    new_quantity: int
    reason: str
    note: str | None = None
    timestamp: datetime
