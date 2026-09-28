import uuid
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from lifeline.models.user import User
from lifeline.models.held_sale import HeldSale

router = APIRouter(prefix="/api/v1/held-sales", tags=["Held Sales"])


@router.get("/")
def list_held_sales(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(HeldSale).order_by(HeldSale.created_at.desc()).all()
    return [
        {"held_sale_id": str(r.held_sale_id), "label": r.label, "created_at": r.created_at, "cart": r.cart_snapshot}
        for r in rows
    ]


@router.post("/", status_code=status.HTTP_201_CREATED)
def hold_sale(label: str, cart_snapshot: dict = Body(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    held = HeldSale(label=label, cart_snapshot=cart_snapshot, created_by=current_user.user_id)
    db.add(held)
    db.commit()
    db.refresh(held)
    return {"held_sale_id": str(held.held_sale_id)}


@router.post("/{held_sale_id}/resume")
def resume_sale(held_sale_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    held = db.query(HeldSale).filter(HeldSale.held_sale_id == held_sale_id).first()
    if not held:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Held sale not found — it may have already been resumed.")
    cart = held.cart_snapshot
    db.delete(held)
    db.commit()
    return {"cart": cart}
