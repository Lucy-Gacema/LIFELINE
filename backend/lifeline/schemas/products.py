import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    product_name: str = Field(..., min_length=1)
    selling_price: Decimal = Field(..., gt=0)
    current_stock: int = Field(..., ge=0)

    sku: str | None = None
    barcode: str | None = None
    category_id: uuid.UUID | None = None
    unit: str | None = "pc"
    buying_price: Decimal | None = Field(None, gt=0)
    tax_rate: Decimal | None = Field(0, ge=0, le=100)
    minimum_stock: int | None = Field(0, ge=0)
    maximum_stock: int | None = Field(None, ge=0)
    supplier_id: uuid.UUID | None = None
    image_url: str | None = None
    aliases: list[str] | None = Field(default_factory=list)


class ProductUpdate(BaseModel):
    product_name: str | None = None
    selling_price: Decimal | None = Field(None, gt=0)
    sku: str | None = None
    barcode: str | None = None
    category_id: uuid.UUID | None = None
    unit: str | None = None
    buying_price: Decimal | None = Field(None, ge=0)
    tax_rate: Decimal | None = Field(None, ge=0, le=100)
    minimum_stock: int | None = Field(None, ge=0)
    maximum_stock: int | None = Field(None, ge=0)
    supplier_id: uuid.UUID | None = None
    image_url: str | None = None
    aliases: list[str] | None = None
    is_favorite: bool | None = None
    is_active: bool | None = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: uuid.UUID
    product_name: str
    sku: str | None = None
    barcode: str | None = None
    category_id: uuid.UUID | None = None
    unit: str
    buying_price: Decimal | None = None
    selling_price: Decimal
    tax_rate: Decimal
    current_stock: int
    minimum_stock: int
    maximum_stock: int | None = None
    supplier_id: uuid.UUID | None = None
    image_url: str | None = None
    aliases: list[str] | None = None
    is_favorite: bool
    is_active: bool
    stock_status: str


class CategoryCreate(BaseModel):
    name: str
    icon: str | None = None


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    category_id: uuid.UUID
    name: str
    icon: str | None = None
