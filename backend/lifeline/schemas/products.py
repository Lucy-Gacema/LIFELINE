import uuid
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    
    product_name: str
    selling_price: Decimal
    current_stock: int = 0

    sku: Optional[str] = None
    barcode: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    unit: Optional[str] = "pc"
    buying_price: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = 0
    minimum_stock: Optional[int] = 0
    maximum_stock: Optional[int] = None
    supplier_id: Optional[uuid.UUID] = None
    image_url: Optional[str] = None
    aliases: Optional[List[str]] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    selling_price: Optional[Decimal] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    unit: Optional[str] = None
    buying_price: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    minimum_stock: Optional[int] = None
    maximum_stock: Optional[int] = None
    supplier_id: Optional[uuid.UUID] = None
    image_url: Optional[str] = None
    aliases: Optional[List[str]] = None
    is_favorite: Optional[bool] = None
    is_active: Optional[bool] = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: uuid.UUID
    product_name: str
    sku: Optional[str] = None
    barcode: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    unit: str
    buying_price: Optional[Decimal] = None
    selling_price: Decimal
    tax_rate: Decimal
    current_stock: int
    minimum_stock: int
    maximum_stock: Optional[int] = None
    supplier_id: Optional[uuid.UUID] = None
    image_url: Optional[str] = None
    aliases: Optional[List[str]] = None
    is_favorite: bool
    is_active: bool
    stock_status: str


class CategoryCreate(BaseModel):
    name: str
    icon: Optional[str] = None


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    category_id: uuid.UUID
    name: str
    icon: Optional[str] = None
