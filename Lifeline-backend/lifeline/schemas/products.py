from pydantic import BaseModel
from decimal import Decimal
import uuid
from typing import Optional

class ProductBase(BaseModel):
    product_name : str
    buying_price : Decimal
    selling_price : Decimal
    current_stock : int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    product_name :Optional[ str] =None
    buying_price :Optional[Decimal]=None
    selling_price :Optional[Decimal] =None
    current_stock :  Optional[int] =None

class ProductResponse(ProductBase):
    product_id: uuid.UUID

    class Config:
        from_attributes = True

