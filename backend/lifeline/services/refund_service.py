from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from lifeline.models.product import Product
from lifeline.models.refund import Refund, RefundItem
from lifeline.models.sale import Sale, SaleStatus
from lifeline.models.sale_item import SaleItem
from lifeline.schemas.inventory_logs import ReasonEnum
from lifeline.schemas.sales import RefundCreate
from lifeline.services import audit_service, inventory_service


def create_refund(db: Session, data: RefundCreate, user) -> Refund:
    sale = db.query(Sale).filter(Sale.sale_id == data.sale_id).first()
    if not sale:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Original transaction not found."
        )
    if sale.status == SaleStatus.CANCELLED:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "This sale was already voided."
        )

    total_refund = Decimal(0)
    refund_items = []

    for ri in data.items:
        sale_item = (
            db.query(SaleItem)
            .filter(
                SaleItem.sale_item_id == ri.sale_item_id,
                SaleItem.sale_id == sale.sale_id,
            )
            .first()
        )
        if not sale_item:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "One of the items was not found on that receipt.",
            )

        already_refunded = sale_item.quantity_refunded
        if already_refunded + ri.quantity > sale_item.quantity:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Cannot refund {ri.quantity} of '{sale_item.item_name}' — only "
                f"{sale_item.quantity - already_refunded} remain un-refunded on this receipt.",
            )

        unit_refund = sale_item.line_total / sale_item.quantity
        amount = unit_refund * ri.quantity
        total_refund += amount

        sale_item.quantity_refunded += ri.quantity
        refund_items.append(
            RefundItem(
                sale_item_id=sale_item.sale_item_id, quantity=ri.quantity, amount=amount
            )
        )

        if sale_item.product_id:
            product = (
                db.query(Product)
                .filter(Product.product_id == sale_item.product_id)
                .first()
            )
            if product:
                inventory_service.adjust_stock(
                    db,
                    product,
                    ri.quantity,
                    ReasonEnum.RETURN,
                    user_id=user.user_id,
                    note="Customer return",
                    commit=False,
                )

    refund = Refund(
        sale_id=sale.sale_id,
        processed_by=user.user_id,
        refund_method=data.refund_method,
        total_amount=total_refund,
        reason=data.reason,
    )
    refund.items = refund_items
    db.add(refund)

    all_refunded = all(i.quantity_refunded >= i.quantity for i in sale.items)
    sale.status = SaleStatus.REFUNDED if all_refunded else SaleStatus.PARTIALLY_REFUNDED

    audit_service.log_action(
        db,
        user_id=user.user_id,
        action="refund.issued",
        entity_type="sale",
        entity_id=sale.sale_id,
        new_value={"amount": float(total_refund)},
        reason=data.reason,
        commit=False,
    )

    db.commit()
    db.refresh(refund)
    return refund
