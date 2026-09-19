from pydantic import BaseModel, model_validator
from datetime import datetime
from decimal import Decimal
import enum
import uuid
from typing import Optional

class PaymentMethodEnum(str, enum.Enum):
    MPESA = "Mpesa"
    CASH = "Cash"
    CREDIT = "Credit"


class SaleBase(BaseModel):
    product_id : uuid.UUID
    quantity_sold : int
    payment_method : PaymentMethodEnum

class SaleCreate(SaleBase):
    pass

class SaleUpdate(BaseModel):
    product_id : Optional[uuid.UUID] = None
    quantity_sold : Optional[int] = None
    payment_method : Optional[PaymentMethodEnum] = None

class SaleResponse(SaleBase):
    sale_id : uuid.UUID
    timestamp : datetime
    total_amount : Decimal 
    product_name:str

    @model_validator(mode="before")
    @classmethod
    def extract_product_name(cls, data):
        if hasattr(data, "product") and data.product:
            setattr(data, "product_name", data.product.product_name)
        
        elif isinstance(data, dict):
            product_obj = data.get("product")
            if product_obj:
                data["product_name"] = (
                    product_obj.product_name 
                    if hasattr(product_obj, "product_name") 
                    else product_obj.get("product_name")
                )
        return data

    class Config:
        from_attributes = True
