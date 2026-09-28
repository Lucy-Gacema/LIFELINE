import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_permission
from lifeline.models.user import User
from lifeline.models.shift import Shift, ShiftStatus
from lifeline.schemas.shifts import ShiftOpen, ShiftClose, ShiftOut, CashMovementCreate
from lifeline.services import cash_service

router = APIRouter(prefix="/api/v1/shifts", tags=["Shifts & Cash Drawer"])


@router.post("/open", response_model=ShiftOut, status_code=status.HTTP_201_CREATED)
def open_shift(data: ShiftOpen, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return cash_service.open_shift(db, data, current_user)


@router.get("/current", response_model=ShiftOut)
def current_shift(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    shift = db.query(Shift).filter(Shift.cashier_id == current_user.user_id, Shift.status == ShiftStatus.OPEN).first()
    if not shift:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No open shift. Open one to start selling.")
    return shift


@router.get("/{shift_id}/expected-cash")
def expected_cash(shift_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    shift = db.query(Shift).filter(Shift.shift_id == shift_id).first()
    if not shift:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Shift not found.")
    return {"expected_cash": float(cash_service.get_expected_cash(db, shift))}


@router.post("/{shift_id}/close", response_model=ShiftOut)
def close_shift(shift_id: uuid.UUID, data: ShiftClose, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    shift = db.query(Shift).filter(Shift.shift_id == shift_id).first()
    if not shift:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Shift not found.")
    return cash_service.close_shift(db, shift, data, current_user)


@router.post("/{shift_id}/cash-movement", status_code=status.HTTP_201_CREATED)
def record_cash_movement(shift_id: uuid.UUID, data: CashMovementCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    shift = db.query(Shift).filter(Shift.shift_id == shift_id).first()
    if not shift:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Shift not found.")
    movement = cash_service.record_cash_movement(db, shift, data, current_user)
    return {"cash_movement_id": str(movement.cash_movement_id), "type": movement.type, "amount": float(movement.amount)}
