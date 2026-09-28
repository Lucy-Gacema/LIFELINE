import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_permission
from lifeline.models.user import User
from lifeline.models.product import Product
from lifeline.models.inventory_logs import InventoryLogs
from lifeline.schemas.inventory import InventoryAdjustment, InventoryLogOut
from lifeline.services import inventory_service
from lifeline.services.inventory_service import InsufficientStockError

router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory"])


@router.post("/adjust", response_model=InventoryLogOut)
def adjust_inventory(data: InventoryAdjustment, db: Session = Depends(get_db), current_user: User = Depends(require_permission("adjust_inventory"))):
    product = db.query(Product).filter(Product.product_id == data.product_id).first()
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found.")
    try:
        log = inventory_service.adjust_stock(
            db, product, data.quantity_changed, data.reason,
            user_id=current_user.user_id, note=data.note, allow_negative_stock=data.allow_negative_stock,
        )
    except InsufficientStockError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    return log


@router.get("/logs", response_model=list[InventoryLogOut])
def list_logs(product_id: uuid.UUID = None, limit: int = 200, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(InventoryLogs)
    if product_id:
        query = query.filter(InventoryLogs.product_id == product_id)
    return query.order_by(InventoryLogs.timestamp.desc()).limit(limit).all()
