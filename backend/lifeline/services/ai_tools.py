import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from lifeline.models.product import Product
from lifeline.models.sale import Sale
from lifeline.models.shift import Shift, ShiftStatus
from lifeline.schemas.customers import CustomerCreate
from lifeline.schemas.expenses import ExpenseCreate
from lifeline.schemas.inventory_logs import ReasonEnum
from lifeline.schemas.sales import PaymentIn, PaymentMethodEnum, SaleCreate, SaleItemIn
from lifeline.services import (
    customer_service,
    expense_service,
    inventory_service,
    product_service,
    report_service,
    sale_service,
)

RISK_LEVELS = {
    "lookup_product": "low",
    "check_inventory": "low",
    "lookup_customer": "low",
    "lookup_transaction": "low",
    "get_sales_summary": "low",
    "get_profit_summary": "low",
    "get_low_stock_products": "low",
    "get_top_products": "low",
    "get_cash_drawer_status": "low",
    "calculate_cart": "low",
    "get_business_health": "low",
    "create_customer": "medium",
    "adjust_inventory": "medium",
    "create_expense": "medium",
    "create_sale": "high",
    "create_return": "high",
}

TOOL_PERMISSIONS = {
    "get_profit_summary": "view_profit",
    "adjust_inventory": "adjust_inventory",
    "create_return": "refund_sale",
    "create_expense": "manage_expenses",
    "create_customer": "manage_customers",
}


class ToolError(Exception):
    """A user-facing error from a tool call — safe to show verbatim in chat."""


def _require_permission(user, tool_name: str):
    permission = TOOL_PERMISSIONS.get(tool_name)
    if permission and not user.has_permission(permission):
        raise ToolError(f"You don't have permission to do this ({permission}).")


def lookup_product(db: Session, user, query: str) -> dict:
    matches = product_service.find_product_by_lookup(db, query)
    if not matches:
        return {"found": False, "matches": []}
    return {
        "found": True,
        "matches": [
            {
                "product_id": str(p.product_id),
                "name": p.product_name,
                "price": float(p.selling_price),
                "current_stock": p.current_stock,
                "unit": p.unit,
            }
            for p in matches[:8]
        ],
    }


def check_inventory(db: Session, user, product_query: str) -> dict:
    result = lookup_product(db, user, product_query)
    return result


def lookup_customer(db: Session, user, query: str) -> dict:
    matches = customer_service.search_customers(db, query)
    return {
        "found": bool(matches),
        "matches": [
            {
                "customer_id": str(c.customer_id),
                "name": c.name,
                "phone": c.phone,
                "outstanding_balance": float(c.outstanding_balance),
            }
            for c in matches[:8]
        ],
    }


def lookup_transaction(
    db: Session, user, receipt_number: str | None = None, sale_id: str | None = None
) -> dict:
    query = db.query(Sale)
    if sale_id:
        sale = query.filter(Sale.sale_id == sale_id).first()
    elif receipt_number:
        sale = query.filter(Sale.receipt_number == receipt_number).first()
    else:
        raise ToolError("I need a receipt number or transaction ID to look that up.")
    if not sale:
        return {"found": False}
    return {
        "found": True,
        "sale_id": str(sale.sale_id),
        "receipt_number": sale.receipt_number,
        "total_amount": float(sale.total_amount),
        "status": sale.status if isinstance(sale.status, str) else sale.status.value,
        "timestamp": sale.timestamp.isoformat(),
        "items": [
            {
                "name": i.item_name,
                "quantity": i.quantity,
                "line_total": float(i.line_total),
                "sale_item_id": str(i.sale_item_id),
            }
            for i in sale.items
        ],
    }


def get_sales_summary(db: Session, user, period: str = "today") -> dict:
    return report_service.get_sales_summary(db, period)


def get_profit_summary(db: Session, user, period: str = "today") -> dict:
    _require_permission(user, "get_profit_summary")
    return report_service.get_profit_summary(db, period)


def get_low_stock_products(db: Session, user) -> dict:
    products = product_service.get_low_stock_products(db)
    return {
        "products": [
            {
                "name": p.product_name,
                "current_stock": p.current_stock,
                "minimum_stock": p.minimum_stock,
            }
            for p in products
        ]
    }


def get_top_products(
    db: Session, user, period: str = "today", by: str = "quantity", limit: int = 5
) -> dict:
    return {"products": report_service.get_top_products(db, period, limit=limit, by=by)}


def get_cash_drawer_status(db: Session, user) -> dict:
    shift = (
        db.query(Shift)
        .filter(Shift.cashier_id == user.user_id, Shift.status == ShiftStatus.OPEN)
        .first()
    )
    if not shift:
        raise ToolError(
            "You don't have an open shift right now, so there's no drawer to check."
        )
    return report_service.get_cash_drawer_status(db, shift)


def get_business_health(db: Session, user) -> dict:
    return report_service.get_business_health_snapshot(db)


def calculate_cart(db: Session, user, items: list) -> dict:

    resolved = []
    total = Decimal(0)
    ambiguous = []
    not_found = []

    for raw in items:
        qty = int(raw.get("quantity", 1))
        product = None
        if raw.get("product_id"):
            product = (
                db.query(Product)
                .filter(Product.product_id == raw["product_id"])
                .first()
            )
        elif raw.get("product_name"):
            matches = product_service.find_product_by_lookup(db, raw["product_name"])
            if len(matches) == 1:
                product = matches[0]
            elif len(matches) > 1:
                ambiguous.append(
                    {
                        "query": raw["product_name"],
                        "options": [
                            {
                                "product_id": str(m.product_id),
                                "name": m.product_name,
                                "price": float(m.selling_price),
                            }
                            for m in matches
                        ],
                    }
                )
                continue
            else:
                not_found.append(raw["product_name"])
                continue

        if not product:
            continue

        line_total = product.selling_price * qty
        total += line_total
        resolved.append(
            {
                "product_id": str(product.product_id),
                "name": product.product_name,
                "quantity": qty,
                "unit_price": float(product.selling_price),
                "line_total": float(line_total),
                "current_stock": product.current_stock,
            }
        )

    return {
        "resolved_items": resolved,
        "ambiguous": ambiguous,
        "not_found": not_found,
        "total": float(total),
    }


def create_customer(db: Session, user, name: str, phone: str | None = None) -> dict:
    _require_permission(user, "create_customer")
    customer = customer_service.create_customer(
        db, CustomerCreate(name=name, phone=phone)
    )
    return {"customer_id": str(customer.customer_id), "name": customer.name}


def adjust_inventory(
    db: Session,
    user,
    product_query: str,
    quantity_changed: int,
    reason: str,
    note: str | None = None,
) -> dict:
    _require_permission(user, "adjust_inventory")
    matches = product_service.find_product_by_lookup(db, product_query)
    if not matches:
        raise ToolError(f"I couldn't find a product matching '{product_query}'.")
    if len(matches) > 1:
        raise ToolError("More than one product matches that — please be more specific.")
    product = matches[0]
    try:
        reason_enum = ReasonEnum(reason)
    except ValueError:
        reason_enum = ReasonEnum.CORRECTION
    log = inventory_service.adjust_stock(
        db, product, quantity_changed, reason_enum, user_id=user.user_id, note=note
    )
    return {
        "product": product.product_name,
        "previous_quantity": log.previous_quantity,
        "new_quantity": log.new_quantity,
    }


def create_expense(
    db: Session,
    user,
    category: str,
    amount: float,
    note: str | None = None,
    payment_method: str = "cash",
) -> dict:
    _require_permission(user, "create_expense")
    expense = expense_service.create_expense(
        db,
        ExpenseCreate(
            category=category,
            amount=Decimal(str(amount)),
            note=note,
            payment_method=payment_method,
        ),
        user,
    )
    return {
        "expense_id": str(expense.expense_id),
        "category": expense.category,
        "amount": float(expense.amount),
    }


def create_sale(
    db: Session,
    user,
    items: list,
    payments: list,
    customer_id: str | None = None,
    idempotency_key: str | None = None,
    note: str | None = None,
) -> dict:
    sale_items = [
        SaleItemIn(
            product_id=i.get("product_id"),
            product_name=i.get("product_name"),
            quantity=int(i["quantity"]),
            unit_price=Decimal(str(i["unit_price"]))
            if i.get("unit_price") is not None
            else None,
        )
        for i in items
    ]
    payment_items = [
        PaymentIn(
            method=PaymentMethodEnum(p["method"]),
            amount=Decimal(str(p["amount"])),
            amount_tendered=Decimal(str(p["amount_tendered"]))
            if p.get("amount_tendered") is not None
            else None,
            transaction_reference=p.get("transaction_reference"),
        )
        for p in payments
    ]
    data = SaleCreate(
        idempotency_key=idempotency_key or str(uuid.uuid4()),
        items=sale_items,
        payments=payment_items,
        customer_id=customer_id,
        note=note,
        created_via="ai_chat",
    )
    sale = sale_service.create_sale(db, data, user)
    return {
        "sale_id": str(sale.sale_id),
        "receipt_number": sale.receipt_number,
        "total_amount": float(sale.total_amount),
    }


def create_return(
    db: Session, user, sale_id: str, sale_item_ids_quantities: list, reason: str
) -> dict:
    from lifeline.schemas.sales import RefundCreate, RefundItemIn
    from lifeline.services import refund_service

    data = RefundCreate(
        sale_id=sale_id,
        items=[
            RefundItemIn(sale_item_id=x["sale_item_id"], quantity=x["quantity"])
            for x in sale_item_ids_quantities
        ],
        reason=reason,
    )
    refund = refund_service.create_refund(db, data, user)
    return {
        "refund_id": str(refund.refund_id),
        "total_amount": float(refund.total_amount),
    }


TOOL_FUNCTIONS = {
    "lookup_product": lookup_product,
    "check_inventory": check_inventory,
    "lookup_customer": lookup_customer,
    "lookup_transaction": lookup_transaction,
    "get_sales_summary": get_sales_summary,
    "get_profit_summary": get_profit_summary,
    "get_low_stock_products": get_low_stock_products,
    "get_top_products": get_top_products,
    "get_cash_drawer_status": get_cash_drawer_status,
    "get_business_health": get_business_health,
    "calculate_cart": calculate_cart,
    "create_customer": create_customer,
    "adjust_inventory": adjust_inventory,
    "create_expense": create_expense,
    "create_sale": create_sale,
    "create_return": create_return,
}
