from database import Base, engine
from lifeline.models.audit_log import AuditLog
from lifeline.models.business_setting import BusinessSetting
from lifeline.models.cash_movement import CashMovement
from lifeline.models.category import Category
from lifeline.models.customer import Customer
from lifeline.models.customer_credit import CustomerCredit
from lifeline.models.expense import Expense
from lifeline.models.goods_received_note import GoodsReceivedNote, GoodsReceivedNoteItem
from lifeline.models.held_sale import HeldSale
from lifeline.models.inventory_logs import InventoryLogs
from lifeline.models.payment import Payment
from lifeline.models.product import Product
from lifeline.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from lifeline.models.refund import Refund, RefundItem
from lifeline.models.sale import Sale
from lifeline.models.sale_item import SaleItem
from lifeline.models.shift import Shift
from lifeline.models.supplier import Supplier
from lifeline.models.sync_operation import SyncOperation
from lifeline.models.user import User

__all__ = [
    "AuditLog",
    "BusinessSetting",
    "CashMovement",
    "Category",
    "Customer",
    "CustomerCredit",
    "Expense",
    "GoodsReceivedNote",
    "GoodsReceivedNoteItem",
    "HeldSale",
    "InventoryLogs",
    "Payment",
    "Product",
    "PurchaseOrder",
    "PurchaseOrderItem",
    "Refund",
    "RefundItem",
    "Sale",
    "SaleItem",
    "Shift",
    "Supplier",
    "SyncOperation",
    "User",
]


def create_tables():
    Base.metadata.create_all(bind=engine)
