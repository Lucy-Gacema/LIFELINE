from database import Base, engine

from lifeline.models.user import User
from lifeline.models.category import Category
from lifeline.models.product import Product
from lifeline.models.customer import Customer
from lifeline.models.customer_credit import CustomerCredit
from lifeline.models.supplier import Supplier
from lifeline.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from lifeline.models.goods_received_note import GoodsReceivedNote, GoodsReceivedNoteItem
from lifeline.models.sale import Sale
from lifeline.models.sale_item import SaleItem
from lifeline.models.payment import Payment
from lifeline.models.refund import Refund, RefundItem
from lifeline.models.shift import Shift
from lifeline.models.cash_movement import CashMovement
from lifeline.models.expense import Expense
from lifeline.models.held_sale import HeldSale
from lifeline.models.audit_log import AuditLog
from lifeline.models.business_setting import BusinessSetting
from lifeline.models.sync_operation import SyncOperation
from lifeline.models.inventory_logs import InventoryLogs

__all__ = [
    "User",
    "Category",
    "Product",
    "Customer",
    "CustomerCredit",
    "Supplier",
    "PurchaseOrder",
    "PurchaseOrderItem",
    "GoodsReceivedNote",
    "GoodsReceivedNoteItem",
    "Sale",
    "SaleItem",
    "Payment",
    "Refund",
    "RefundItem",
    "Shift",
    "CashMovement",
    "Expense",
    "HeldSale",
    "AuditLog",
    "BusinessSetting",
    "SyncOperation",
    "InventoryLogs",
]


def create_tables():
    Base.metadata.create_all(bind=engine)
