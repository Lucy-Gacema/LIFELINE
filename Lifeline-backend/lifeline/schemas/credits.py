import uuid
from pydantic import BaseModel, model_validator
from datetime import datetime
from decimal import Decimal
from typing import Optional

class CreditBase(BaseModel):
    sale_id : uuid.UUID
    customer_name : str
    amount_owed : Decimal
    is_paid: bool
    date_borrowed: datetime

class CreditCreate(CreditBase):
    pass

class CreditUpdate(BaseModel):
    sale_id :Optional[uuid.UUID ]=None
    customer_name :Optional[str] =None
    amount_owed :Optional[ Decimal] =None
    is_paid:Optional[ bool] =None
    date_borrowed: Optional[datetime] =None

class CreditResponse(CreditBase):
    credit_id:uuid.UUID 
    item_name: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def extract_item_name(cls, data):
        if hasattr(data, "sale") and data.sale:
            item_name_val = getattr(data.sale, "item_name", None)
            setattr(data, "item_name", item_name_val)
        
        elif isinstance(data, dict):
            sale_obj = data.get("sale")
            if sale_obj:
                data["item_name"] = (
                    sale_obj.item_name 
                    if hasattr(sale_obj, "item_name") 
                    else sale_obj.get("item_name")
                )
        return data

    class Config:
        from_attributes = True





