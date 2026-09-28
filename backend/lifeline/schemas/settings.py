from typing import Optional
from decimal import Decimal
from pydantic import BaseModel


class BusinessSettingsUpdate(BaseModel):
    business_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    tax_number: Optional[str] = None
    currency: Optional[str] = None
    tax_rate: Optional[Decimal] = None
    receipt_footer: Optional[str] = None
    low_stock_threshold: Optional[int] = None
    allow_negative_stock: Optional[bool] = None
    require_manager_approval_for_refunds: Optional[bool] = None
    max_discount_percent_without_approval: Optional[Decimal] = None


class BusinessSettingsOut(BaseModel):
    business_name: str = "My Shop"
    address: Optional[str] = None
    phone: Optional[str] = None
    tax_number: Optional[str] = None
    currency: str = "KES"
    tax_rate: Decimal = Decimal("0")
    receipt_footer: Optional[str] = None
    low_stock_threshold: int = 5
    allow_negative_stock: bool = False
    require_manager_approval_for_refunds: bool = True
    max_discount_percent_without_approval: Decimal = Decimal("10")
