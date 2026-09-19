from pydantic import BaseModel, model_validator
from datetime import datetime
import uuid
import enum
from typing import Optional

class ReasonEnum(str, enum.Enum):
    RESTOCK = "Restock"
    DAMAGED = "Damaged"
    EXPIRED = "Expired"

class InventoryLogBase(BaseModel):
    product_id: uuid.UUID
    quantity_changed: int
    reason: ReasonEnum

class InventoryLogCreate(InventoryLogBase):
    pass

class InventoryLogUpdate(BaseModel):
    product_id: Optional[uuid.UUID] = None
    quantity_changed: Optional[int] = None
    reason: Optional[ReasonEnum] = None

class InventoryLogResponse(BaseModel):
    inventory_logs_id: uuid.UUID
    product_id: uuid.UUID
    quantity_changed: int
    reason: ReasonEnum
    timestamp: datetime
    product_name: str

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if hasattr(obj, "product") and obj.product:
            setattr(obj, "product_name", getattr(obj.product, "product_name", "Unknown Product"))
        elif isinstance(obj, dict):
            prod = obj.get("product", {})
            obj["product_name"] = prod.get("product_name") if isinstance(prod, dict) else getattr(prod, "product_name", "Unknown Product")
            
        return super().model_validate(obj, **kwargs)

    class Config:
        from_attributes = True
