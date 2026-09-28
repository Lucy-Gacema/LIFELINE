import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_permission
from lifeline.models.user import User
from lifeline.models.sale import Sale
from lifeline.schemas.sales import SaleCreate, SaleOut, RefundCreate
from lifeline.services import sale_service, refund_service

router = APIRouter(prefix="/api/v1/sales", tags=["Sales"])


@router.post("/", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
def create_sale(data: SaleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    return sale_service.create_sale(db, data, current_user)


@router.get("/", response_model=list[SaleOut])
def list_sales(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    cashier_id: Optional[uuid.UUID] = None,
    customer_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Sale)
    if date_from:
        query = query.filter(Sale.timestamp >= date_from)
    if date_to:
        query = query.filter(Sale.timestamp <= date_to)
    if cashier_id:
        query = query.filter(Sale.cashier_id == cashier_id)
    if customer_id:
        query = query.filter(Sale.customer_id == customer_id)
    if status_filter:
        query = query.filter(Sale.status == status_filter)
    return query.order_by(Sale.timestamp.desc()).limit(limit).all()


@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sale = db.query(Sale).filter(Sale.sale_id == sale_id).first()
    if not sale:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transaction not found.")
    return sale


@router.post("/{sale_id}/void", response_model=SaleOut)
def void_sale(sale_id: uuid.UUID, reason: str, db: Session = Depends(get_db), current_user: User = Depends(require_permission("void_transaction"))):
    sale = db.query(Sale).filter(Sale.sale_id == sale_id).first()
    if not sale:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transaction not found.")
    return sale_service.void_sale(db, sale, current_user, reason)


@router.post("/refunds", status_code=status.HTTP_201_CREATED)
def create_refund(data: RefundCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permission("refund_sale"))):
    refund = refund_service.create_refund(db, data, current_user)
    return {
        "refund_id": str(refund.refund_id),
        "sale_id": str(refund.sale_id),
        "total_amount": float(refund.total_amount),
        "reason": refund.reason,
    }
