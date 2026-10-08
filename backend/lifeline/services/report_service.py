from datetime import datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from lifeline.models.customer import Customer
from lifeline.models.expense import Expense
from lifeline.models.product import Product
from lifeline.models.sale import Sale, SaleStatus
from lifeline.models.sale_item import SaleItem
from lifeline.models.supplier import Supplier


def resolve_period(
    period: str, reference: datetime | None = None
) -> tuple[datetime, datetime, str]:

    now = reference or datetime.utcnow()
    today_start = datetime.combine(now.date(), time.min)

    if period in ("today", "", None):
        return today_start, today_start + timedelta(days=1), "Today"
    if period == "yesterday":
        start = today_start - timedelta(days=1)
        return start, today_start, "Yesterday"
    if period == "this_week":
        start = today_start - timedelta(days=now.weekday())
        return start, today_start + timedelta(days=1), "This week"
    if period == "last_week":
        this_week_start = today_start - timedelta(days=now.weekday())
        start = this_week_start - timedelta(days=7)
        return start, this_week_start, "Last week"
    if period == "this_month":
        start = today_start.replace(day=1)
        return start, today_start + timedelta(days=1), "This month"
    if period == "last_month":
        first_this_month = today_start.replace(day=1)
        last_month_end = first_this_month
        last_month_start = (first_this_month - timedelta(days=1)).replace(day=1)
        return last_month_start, last_month_end, "Last month"
    # default fallback
    return today_start, today_start + timedelta(days=1), "Today"


def get_sales_summary(db: Session, period: str = "today") -> dict:
    start, end, label = resolve_period(period)
    sales = (
        db.query(Sale)
        .filter(
            Sale.timestamp >= start,
            Sale.timestamp < end,
            Sale.status.in_([SaleStatus.COMPLETED, SaleStatus.PARTIALLY_REFUNDED]),
        )
        .all()
    )
    total_sales = sum((s.total_amount for s in sales), Decimal(0))
    transaction_count = len(sales)
    avg_transaction = (
        (total_sales / transaction_count) if transaction_count else Decimal(0)
    )

    payment_breakdown = {}
    for s in sales:
        for p in s.payments:
            payment_breakdown[
                p.method.value if hasattr(p.method, "value") else p.method
            ] = (
                payment_breakdown.get(
                    p.method.value if hasattr(p.method, "value") else p.method,
                    Decimal(0),
                )
                + p.amount
            )

    return {
        "period": label,
        "range_start": start.isoformat(),
        "range_end": end.isoformat(),
        "total_sales": float(total_sales),
        "transaction_count": transaction_count,
        "average_transaction": float(avg_transaction),
        "payment_breakdown": {k: float(v) for k, v in payment_breakdown.items()},
    }


def get_profit_summary(db: Session, period: str = "today") -> dict:
    start, end, label = resolve_period(period)
    items = (
        db.query(SaleItem)
        .join(Sale, Sale.sale_id == SaleItem.sale_id)
        .filter(
            Sale.timestamp >= start,
            Sale.timestamp < end,
            Sale.status.in_([SaleStatus.COMPLETED, SaleStatus.PARTIALLY_REFUNDED]),
        )
        .all()
    )
    revenue = Decimal(0)
    cost = Decimal(0)
    for item in items:
        revenue += item.line_total
        buying_price = (
            item.product.buying_price
            if item.product and item.product.buying_price
            else Decimal(0)
        )
        cost += buying_price * item.quantity

    gross_profit = revenue - cost
    return {
        "period": label,
        "revenue": float(revenue),
        "estimated_cost": float(cost),
        "gross_profit": float(gross_profit),
        "note": "Cost is based on the buying price currently recorded per product; historical cost changes are not tracked.",
    }


def get_top_products(
    db: Session, period: str = "today", limit: int = 5, by: str = "quantity"
) -> list:
    start, end, label = resolve_period(period)
    items = (
        db.query(SaleItem)
        .join(Sale, Sale.sale_id == SaleItem.sale_id)
        .filter(
            Sale.timestamp >= start,
            Sale.timestamp < end,
            Sale.status.in_([SaleStatus.COMPLETED, SaleStatus.PARTIALLY_REFUNDED]),
        )
        .all()
    )
    agg = {}
    for item in items:
        key = item.product_id or item.product_name_snapshot
        row = agg.setdefault(
            key,
            {
                "name": item.item_name,
                "quantity": 0,
                "revenue": Decimal(0),
                "profit": Decimal(0),
            },
        )
        row["quantity"] += item.quantity
        row["revenue"] += item.line_total
        buying_price = (
            item.product.buying_price
            if item.product and item.product.buying_price
            else Decimal(0)
        )
        row["profit"] += item.line_total - (buying_price * item.quantity)

    sort_key = (
        "quantity" if by == "quantity" else ("revenue" if by == "revenue" else "profit")
    )
    ranked = sorted(agg.values(), key=lambda r: r[sort_key], reverse=True)[:limit]
    return [
        {
            "name": r["name"],
            "quantity": r["quantity"],
            "revenue": float(r["revenue"]),
            "profit": float(r["profit"]),
        }
        for r in ranked
    ]


def get_slow_moving_products(db: Session, days: int = 14) -> list:
    cutoff = datetime.utcnow() - timedelta(days=days)
    recent_product_ids = {
        row[0]
        for row in db.query(SaleItem.product_id)
        .join(Sale, Sale.sale_id == SaleItem.sale_id)
        .filter(Sale.timestamp >= cutoff, SaleItem.product_id.isnot(None))
        .distinct()
        .all()
    }
    products = db.query(Product).filter(Product.is_active == True).all()
    return [
        {
            "product_id": str(p.product_id),
            "product_name": p.product_name,
            "current_stock": p.current_stock,
        }
        for p in products
        if p.product_id not in recent_product_ids
    ]


def get_cash_drawer_status(db: Session, shift) -> dict:
    from lifeline.services.cash_service import get_expected_cash

    expected = get_expected_cash(db, shift)
    return {
        "shift_id": str(shift.shift_id),
        "opening_cash": float(shift.opening_cash),
        "expected_cash_now": float(expected),
        "status": shift.status,
    }


def get_expense_summary(db: Session, period: str = "today") -> dict:
    start, end, label = resolve_period(period)
    expenses = db.query(Expense).filter(Expense.date >= start, Expense.date < end).all()
    total = sum((e.amount for e in expenses), Decimal(0))
    by_category = {}
    for e in expenses:
        by_category[e.category] = by_category.get(e.category, Decimal(0)) + e.amount
    return {
        "period": label,
        "total": float(total),
        "by_category": {k: float(v) for k, v in by_category.items()},
        "count": len(expenses),
    }


def get_business_health_snapshot(db: Session) -> dict:

    sales_today = get_sales_summary(db, "today")
    profit_today = get_profit_summary(db, "today")
    top_products = get_top_products(db, "today", limit=3)

    low_stock_products = [
        {
            "product_id": str(p.product_id),
            "name": p.product_name,
            "current_stock": p.current_stock,
            "minimum_stock": p.minimum_stock,
        }
        for p in db.query(Product).filter(Product.is_active == True).all()
        if p.current_stock <= p.minimum_stock
    ]
    outstanding_credit = db.query(
        func.coalesce(func.sum(Customer.outstanding_balance), 0)
    ).scalar()
    supplier_balances = db.query(
        func.coalesce(func.sum(Supplier.amount_owed), 0)
    ).scalar()

    return {
        "today": sales_today,
        "profit_today": profit_today,
        "top_products_today": top_products,
        "low_stock_products": low_stock_products,
        "out_of_stock_count": len(
            [p for p in low_stock_products if p["current_stock"] <= 0]
        ),
        "outstanding_customer_credit": float(outstanding_credit or 0),
        "supplier_balances_owed": float(supplier_balances or 0),
    }
