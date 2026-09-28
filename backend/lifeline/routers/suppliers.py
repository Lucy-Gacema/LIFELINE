import uuid
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_permission
from lifeline.models.user import User
from lifeline.models.supplier import Supplier
from lifeline.models.purchase_order import PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus
from lifeline.schemas.suppliers import SupplierCreate, SupplierOut

router = APIRouter(prefix="/api/v1/suppliers", tags=["Suppliers"])


@router.get("/", response_model=list[SupplierOut])
def list_suppliers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Supplier).order_by(Supplier.name).all()


@router.post("/", response_model=SupplierOut, status_code=status.HTTP_201_CREATED)
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_suppliers"))):
    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier(supplier_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Supplier not found.")
    return supplier


@router.post("/purchase-orders", status_code=status.HTTP_201_CREATED)
def create_purchase_order(supplier_id: uuid.UUID, items: list = Body(...), db: Session = Depends(get_db), current_user: User = Depends(require_permission("manage_suppliers"))):
    """items: [{"product_id": ..., "quantity_ordered": int, "unit_cost": float}]"""
    po = PurchaseOrder(supplier_id=supplier_id, created_by=current_user.user_id, status=PurchaseOrderStatus.ORDERED)
    po.items = [
        PurchaseOrderItem(product_id=i["product_id"], quantity_ordered=i["quantity_ordered"], unit_cost=i["unit_cost"])
        for i in items
    ]
    db.add(po)
    db.commit()
    db.refresh(po)
    return {"purchase_order_id": str(po.purchase_order_id), "status": po.status}


@router.get("/reorder-planner/list")
def reorder_planner(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from lifeline.services import product_service
    low = product_service.get_low_stock_products(db)
    return [
        {
            "product_id": str(p.product_id),
            "product_name": p.product_name,
            "current_stock": p.current_stock,
            "minimum_stock": p.minimum_stock,
            "suggested_reorder_quantity": max((p.maximum_stock or p.minimum_stock * 3) - p.current_stock, p.minimum_stock),
            "supplier_id": str(p.supplier_id) if p.supplier_id else None,
            "last_purchase_price": float(p.buying_price) if p.buying_price else None,
        }
        for p in low
    ]
