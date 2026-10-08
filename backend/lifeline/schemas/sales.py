import enum
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PaymentMethodEnum(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    MPESA = "mpesa"
    QR = "qr"
    WALLET = "wallet"
    STORE_CREDIT = "store_credit"
    CUSTOM = "custom"


class SaleItemIn(BaseModel):
    product_id: uuid.UUID | None = None
    product_name: str | None = None
    quantity: int = Field(..., gt=0)
    unit_price: Decimal | None = Field(None, gt=0)
    discount_amount: Decimal = Field(0, ge=0)


class PaymentIn(BaseModel):
    method: PaymentMethodEnum
    amount: Decimal = Field(..., gt=0)
    amount_tendered: Decimal | None = Field(None, ge=0)
    transaction_reference: str | None = None
    phone_number: str | None = None


class SaleCreate(BaseModel):
    idempotency_key: str
    items: list[SaleItemIn]
    payments: list[PaymentIn]
    customer_id: uuid.UUID | None = None
    discount_total: Decimal = Field(0, ge=0)
    note: str | None = None
    shift_id: uuid.UUID | None = None
    created_via: str = "manual"
    device_id: str | None = None
    allow_negative_stock: bool = False


class SaleItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sale_item_id: uuid.UUID
    product_id: uuid.UUID | None = None
    product_name_snapshot: str
    quantity: int
    unit_price: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    line_total: Decimal
    quantity_refunded: int


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    payment_id: uuid.UUID
    method: str
    amount: Decimal
    amount_tendered: Decimal | None = None
    change_given: Decimal | None = None
    verification_status: str
    transaction_reference: str | None = None


class SaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sale_id: uuid.UUID
    idempotency_key: str
    receipt_number: str | None = None
    customer_id: uuid.UUID | None = None
    cashier_id: uuid.UUID | None = None
    subtotal: Decimal
    discount_total: Decimal
    tax_total: Decimal
    total_amount: Decimal
    status: str
    note: str | None = None
    created_via: str
    timestamp: datetime
    items: list[SaleItemOut] = []
    payments: list[PaymentOut] = []


class RefundItemIn(BaseModel):
    sale_item_id: uuid.UUID
    quantity: int = Field(..., gt=0)


class RefundCreate(BaseModel):
    sale_id: uuid.UUID
    items: list[RefundItemIn]
    reason: str
    refund_method: str = "cash"
