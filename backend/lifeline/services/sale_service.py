import random
import string
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from lifeline.models.customer import Customer
from lifeline.models.customer_credit import CreditTransactionType, CustomerCredit
from lifeline.models.payment import Payment, PaymentMethod, PaymentVerificationStatus
from lifeline.models.product import Product
from lifeline.models.sale import Sale, SaleStatus
from lifeline.models.sale_item import SaleItem
from lifeline.schemas.inventory_logs import ReasonEnum
from lifeline.schemas.sales import SaleCreate
from lifeline.services import audit_service, inventory_service
from lifeline.services.inventory_service import InsufficientStockError


def _generate_receipt_number(db: Session) -> str:
    suffix = "".join(random.choices(string.digits, k=6))
    return f"RCT-{suffix}"


def create_sale(db: Session, data: SaleCreate, cashier) -> Sale:

    existing = (
        db.query(Sale).filter(Sale.idempotency_key == data.idempotency_key).first()
    )
    if existing:
        return existing

    if not data.items:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "A sale must have at least one item."
        )

    subtotal = Decimal(0)
    tax_total = Decimal(0)
    sale_items: list[SaleItem] = []
    stock_mutations = []
    for item_in in data.items:
        product = None
        if item_in.product_id:
            product = (
                db.query(Product)
                .filter(Product.product_id == item_in.product_id)
                .first()
            )
            if not product:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    f"Product not found: {item_in.product_id}",
                )

        unit_price = (
            item_in.unit_price
            if item_in.unit_price is not None
            else (product.selling_price if product else None)
        )
        if unit_price is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"No price given for '{item_in.product_name or product.product_name}'. "
                "What price should be recorded for this item?",
            )

        tax_rate = product.tax_rate if product else Decimal(0)
        line_subtotal = unit_price * item_in.quantity - item_in.discount_amount
        line_tax = (line_subtotal * tax_rate / Decimal(100)) if tax_rate else Decimal(0)
        line_total = line_subtotal + line_tax

        subtotal += unit_price * item_in.quantity
        tax_total += line_tax

        sale_items.append(
            SaleItem(
                product_id=product.product_id if product else None,
                product_name_snapshot=product.product_name
                if product
                else (item_in.product_name or "Custom item"),
                quantity=item_in.quantity,
                unit_price=unit_price,
                discount_amount=item_in.discount_amount,
                tax_amount=line_tax,
                line_total=line_total,
            )
        )

        if product:
            stock_mutations.append((product, item_in.quantity))

    discount_total = data.discount_total
    total_amount = subtotal - discount_total + tax_total

    payments_sum = sum(p.amount for p in data.payments)

    unpaid_amount = total_amount - payments_sum

    if unpaid_amount > Decimal("0.01") and not data.customer_id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Payment does not cover the total and no customer was selected to put the balance on credit.",
        )

    try:
        for product, qty in stock_mutations:
            inventory_service.adjust_stock(
                db,
                product,
                -qty,
                ReasonEnum.SALE,
                user_id=cashier.user_id if cashier else None,
                allow_negative_stock=data.allow_negative_stock,
                commit=False,
            )
    except InsufficientStockError as e:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))

    sale = Sale(
        idempotency_key=data.idempotency_key,
        receipt_number=_generate_receipt_number(db),
        customer_id=data.customer_id,
        cashier_id=cashier.user_id if cashier else None,
        shift_id=data.shift_id,
        subtotal=subtotal,
        discount_total=discount_total,
        tax_total=tax_total,
        total_amount=total_amount,
        status=SaleStatus.COMPLETED,
        note=data.note,
        created_via=data.created_via,
        device_id=data.device_id,
        synced=True,
    )
    sale.items = sale_items
    db.add(sale)
    db.flush()

    for p_in in data.payments:
        change_given = None
        if p_in.method.value == "cash" and p_in.amount_tendered is not None:
            change_given = max(p_in.amount_tendered - p_in.amount, Decimal(0))
        verification = (
            PaymentVerificationStatus.MANUALLY_RECORDED
            if p_in.method.value in ("mpesa", "card", "qr", "wallet", "custom")
            else PaymentVerificationStatus.VERIFIED
        )
        db.add(
            Payment(
                sale_id=sale.sale_id,
                method=PaymentMethod(p_in.method.value),
                amount=p_in.amount,
                amount_tendered=p_in.amount_tendered,
                change_given=change_given,
                verification_status=verification,
                transaction_reference=p_in.transaction_reference,
                phone_number=p_in.phone_number,
                cashier_id=cashier.user_id if cashier else None,
            )
        )

    if unpaid_amount > Decimal("0.01") and data.customer_id:
        customer = (
            db.query(Customer).filter(Customer.customer_id == data.customer_id).first()
        )
        if customer:
            customer.outstanding_balance += unpaid_amount
            db.add(
                CustomerCredit(
                    customer_id=customer.customer_id,
                    sale_id=sale.sale_id,
                    type=CreditTransactionType.CHARGE,
                    amount=unpaid_amount,
                    balance_after=customer.outstanding_balance,
                    note="Balance from sale",
                    created_by=cashier.user_id if cashier else None,
                )
            )

    audit_service.log_action(
        db,
        user_id=cashier.user_id if cashier else None,
        action="sale.created",
        entity_type="sale",
        entity_id=sale.sale_id,
        new_value={"total_amount": float(total_amount)},
        commit=False,
    )

    db.commit()
    db.refresh(sale)
    return sale


def void_sale(db: Session, sale: Sale, user, reason: str) -> Sale:

    if sale.status != SaleStatus.COMPLETED:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Only completed sales can be voided."
        )

    for item in sale.items:
        if item.product_id:
            product = (
                db.query(Product).filter(Product.product_id == item.product_id).first()
            )
            if product:
                inventory_service.adjust_stock(
                    db,
                    product,
                    item.quantity,
                    ReasonEnum.RETURN,
                    user_id=user.user_id,
                    note=f"Void of sale {sale.receipt_number}",
                    commit=False,
                )

    sale.status = SaleStatus.CANCELLED
    audit_service.log_action(
        db,
        user_id=user.user_id,
        action="sale.voided",
        entity_type="sale",
        entity_id=sale.sale_id,
        reason=reason,
        commit=False,
    )
    db.commit()
    db.refresh(sale)
    return sale
