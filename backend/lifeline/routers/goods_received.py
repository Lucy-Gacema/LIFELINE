import uuid

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import require_permission
from lifeline.models.goods_received_note import GoodsReceivedNote, GoodsReceivedNoteItem
from lifeline.models.product import Product
from lifeline.models.purchase_order import PurchaseOrder, PurchaseOrderStatus
from lifeline.models.user import User
from lifeline.schemas.inventory_logs import ReasonEnum
from lifeline.services import inventory_service

router = APIRouter(prefix="/api/v1/goods-received", tags=["Goods Received"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def receive_goods(
    purchase_order_id: uuid.UUID,
    items: list = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_suppliers")),
):

    po = (
        db.query(PurchaseOrder)
        .filter(PurchaseOrder.purchase_order_id == purchase_order_id)
        .first()
    )
    if not po:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Purchase order not found.")

    grn = GoodsReceivedNote(
        purchase_order_id=purchase_order_id, received_by=current_user.user_id
    )
    grn_items = []
    variances = []

    for i in items:
        product = (
            db.query(Product).filter(Product.product_id == i["product_id"]).first()
        )
        if not product:
            continue
        item = GoodsReceivedNoteItem(
            product_id=product.product_id,
            quantity_ordered=i.get("quantity_ordered", 0),
            quantity_received=i["quantity_received"],
        )
        grn_items.append(item)
        if item.variance != 0:
            variances.append(
                {"product": product.product_name, "variance": item.variance}
            )

        inventory_service.adjust_stock(
            db,
            product,
            i["quantity_received"],
            ReasonEnum.RESTOCK,
            user_id=current_user.user_id,
            note=f"GRN for PO {purchase_order_id}",
            commit=False,
        )

    grn.items = grn_items
    po.status = PurchaseOrderStatus.RECEIVED
    db.add(grn)
    db.commit()
    db.refresh(grn)

    return {"grn_id": str(grn.grn_id), "variances": variances}
