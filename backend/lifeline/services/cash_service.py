from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from lifeline.models.cash_movement import CashMovement, CashMovementType
from lifeline.models.payment import Payment, PaymentMethod
from lifeline.models.sale import Sale
from lifeline.models.shift import Shift, ShiftStatus
from lifeline.schemas.shifts import CashMovementCreate, ShiftClose, ShiftOpen
from lifeline.services import audit_service


def open_shift(db: Session, data: ShiftOpen, cashier) -> Shift:
    open_existing = (
        db.query(Shift)
        .filter(Shift.cashier_id == cashier.user_id, Shift.status == ShiftStatus.OPEN)
        .first()
    )
    if open_existing:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "You already have an open shift."
        )

    shift = Shift(cashier_id=cashier.user_id, opening_cash=data.opening_cash)
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


def get_expected_cash(db: Session, shift: Shift) -> Decimal:
    """Opening float + cash sales + cash movements in, minus drops/payouts."""
    cash_sales = (
        db.query(Payment)
        .join(Sale, Sale.sale_id == Payment.sale_id)
        .filter(Sale.shift_id == shift.shift_id, Payment.method == PaymentMethod.CASH)
        .all()
    )
    total_cash_sales = sum((p.amount for p in cash_sales), Decimal(0))

    movements = (
        db.query(CashMovement).filter(CashMovement.shift_id == shift.shift_id).all()
    )
    drops = sum(
        (
            m.amount
            for m in movements
            if m.type in (CashMovementType.DROP, CashMovementType.PAYOUT)
        ),
        Decimal(0),
    )
    adjustments = sum(
        (m.amount for m in movements if m.type == CashMovementType.ADJUSTMENT),
        Decimal(0),
    )

    return shift.opening_cash + total_cash_sales - drops + adjustments


def close_shift(db: Session, shift: Shift, data: ShiftClose, closer) -> Shift:
    if shift.status != ShiftStatus.OPEN:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "This shift is already closed."
        )

    expected = get_expected_cash(db, shift)
    shift.expected_cash = expected
    shift.actual_cash = data.actual_cash
    shift.cash_difference = data.actual_cash - expected
    shift.closing_note = data.closing_note
    shift.status = ShiftStatus.CLOSED
    shift.closed_by_manager_id = closer.user_id

    from datetime import datetime

    shift.closed_at = datetime.utcnow()

    audit_service.log_action(
        db,
        user_id=closer.user_id,
        action="shift.closed",
        entity_type="shift",
        entity_id=shift.shift_id,
        new_value={
            "expected": float(expected),
            "actual": float(data.actual_cash),
            "difference": float(shift.cash_difference),
        },
        commit=False,
    )

    db.commit()
    db.refresh(shift)
    return shift


def record_cash_movement(
    db: Session, shift: Shift, data: CashMovementCreate, user
) -> CashMovement:
    movement = CashMovement(
        shift_id=shift.shift_id,
        type=CashMovementType(data.type),
        amount=data.amount,
        reason=data.reason,
        created_by=user.user_id,
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement
