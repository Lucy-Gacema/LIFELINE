import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
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
    product_id: Optional[uuid.UUID] = None
    product_name: Optional[str] = None  
    quantity: int = Field(..., gt=0)
    unit_price: Optional[Decimal] = None  
    discount_amount: Decimal = 0


class PaymentIn(BaseModel):
    method: PaymentMethodEnum
    amount: Decimal
    amount_tendered: Optional[Decimal] = None
    transaction_reference: Optional[str] = None
    phone_number: Optional[str] = None


class SaleCreate(BaseModel):
    idempotency_key: str
    items: List[SaleItemIn]
    payments: List[PaymentIn]
    customer_id: Optional[uuid.UUID] = None
    discount_total: Decimal = 0
    note: Optional[str] = None
    shift_id: Optional[uuid.UUID] = None
    created_via: str = "manual"
    device_id: Optional[str] = None
    allow_negative_stock: bool = False


class SaleItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sale_item_id: uuid.UUID
    product_id: Optional[uuid.UUID] = None
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
    amount_tendered: Optional[Decimal] = None
    change_given: Optional[Decimal] = None
    verification_status: str
    transaction_reference: Optional[str] = None


class SaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sale_id: uuid.UUID
    idempotency_key: str
    receipt_number: Optional[str] = None
    customer_id: Optional[uuid.UUID] = None
    cashier_id: Optional[uuid.UUID] = None
    subtotal: Decimal
    discount_total: Decimal
    tax_total: Decimal
    total_amount: Decimal
    status: str
    note: Optional[str] = None
    created_via: str
    timestamp: datetime
    items: List[SaleItemOut] = []
    payments: List[PaymentOut] = []


class RefundItemIn(BaseModel):
    sale_item_id: uuid.UUID
    quantity: int = Field(..., gt=0)


class RefundCreate(BaseModel):
    sale_id: uuid.UUID
    items: List[RefundItemIn]
    reason: str
    refund_method: str = "cash"
