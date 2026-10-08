from decimal import Decimal

from pydantic import BaseModel


class BusinessSettingsUpdate(BaseModel):
    business_name: str | None = None
    address: str | None = None
    phone: str | None = None
    tax_number: str | None = None
    currency: str | None = None
    tax_rate: Decimal | None = None
    receipt_footer: str | None = None
    low_stock_threshold: int | None = None
    allow_negative_stock: bool | None = None
    require_manager_approval_for_refunds: bool | None = None
    max_discount_percent_without_approval: Decimal | None = None


class BusinessSettingsOut(BaseModel):
    business_name: str = "My Shop"
    address: str | None = None
    phone: str | None = None
    tax_number: str | None = None
    currency: str = "KES"
    tax_rate: Decimal = Decimal(0)
    receipt_footer: str | None = None
    low_stock_threshold: int = 5
    allow_negative_stock: bool = False
    require_manager_approval_for_refunds: bool = True
    max_discount_percent_without_approval: Decimal = Decimal(10)
