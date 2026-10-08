from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from lifeline.models.product import Product
from lifeline.models.sync_operation import SyncOperation, SyncStatus
from lifeline.models.user import User
from lifeline.schemas.inventory_logs import ReasonEnum
from lifeline.schemas.sales import SaleCreate
from lifeline.schemas.sync import (
    SyncOperationResult,
    SyncPullResponse,
    SyncPushRequest,
    SyncPushResponse,
)
from lifeline.services import inventory_service, sale_service, settings_service

router = APIRouter(prefix="/api/v1/sync", tags=["Offline Sync"])

_HANDLERS = {}


def _handle_create_sale(db: Session, user, payload: dict):
    sale = sale_service.create_sale(db, SaleCreate(**payload), user)
    return str(sale.sale_id)


def _handle_adjust_inventory(db: Session, user, payload: dict):
    from lifeline.models.product import Product

    product = (
        db.query(Product).filter(Product.product_id == payload["product_id"]).first()
    )
    if not product:
        raise ValueError("Product not found")
    log = inventory_service.adjust_stock(
        db,
        product,
        payload["quantity_changed"],
        ReasonEnum(payload["reason"]),
        user_id=user.user_id,
        note=payload.get("note"),
        allow_negative_stock=payload.get("allow_negative_stock", False),
    )
    return str(log.inventory_logs_id)


_HANDLERS["create_sale"] = _handle_create_sale
_HANDLERS["adjust_inventory"] = _handle_adjust_inventory


@router.post("/push", response_model=SyncPushResponse)
def push_operations(
    data: SyncPushRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = []
    for op in data.operations:
        existing = (
            db.query(SyncOperation)
            .filter(SyncOperation.idempotency_key == op.idempotency_key)
            .first()
        )
        if existing and existing.status == SyncStatus.APPLIED:
            results.append(
                SyncOperationResult(
                    idempotency_key=op.idempotency_key, status="already_applied"
                )
            )
            continue

        record = existing or SyncOperation(
            device_id=op.device_id,
            idempotency_key=op.idempotency_key,
            operation_type=op.operation_type,
            payload=op.payload,
        )
        if not existing:
            db.add(record)
            db.flush()

        handler = _HANDLERS.get(op.operation_type)
        if not handler:
            record.status = SyncStatus.FAILED
            record.error_message = f"Unknown operation type: {op.operation_type}"
            db.commit()
            results.append(
                SyncOperationResult(
                    idempotency_key=op.idempotency_key,
                    status="failed",
                    error_message=record.error_message,
                )
            )
            continue

        try:
            server_id = handler(db, current_user, op.payload)
            record.status = SyncStatus.APPLIED
            record.applied_at = datetime.utcnow()
            db.commit()
            results.append(
                SyncOperationResult(
                    idempotency_key=op.idempotency_key,
                    status="applied",
                    server_id=server_id,
                )
            )
        except Exception as e:  # noqa: BLE001
            db.rollback()
            record.status = SyncStatus.FAILED
            record.error_message = str(e)
            db.add(record)
            db.commit()
            results.append(
                SyncOperationResult(
                    idempotency_key=op.idempotency_key,
                    status="failed",
                    error_message=str(e),
                )
            )

    return SyncPushResponse(results=results)


@router.get("/pull", response_model=SyncPullResponse)
def pull_updates(
    since: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cutoff = (
        datetime.fromisoformat(since)
        if since
        else (datetime.utcnow() - timedelta(days=1))
    )
    products = db.query(Product).filter(Product.is_active == True).all()
    return SyncPullResponse(
        server_time=datetime.utcnow().isoformat(),
        products_updated_since=[
            {
                "product_id": str(p.product_id),
                "product_name": p.product_name,
                "selling_price": float(p.selling_price),
                "current_stock": p.current_stock,
            }
            for p in products
        ],
        settings=settings_service.get_settings(db),
    )
