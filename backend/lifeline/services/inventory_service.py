from sqlalchemy.orm import Session

from lifeline.models.inventory_logs import InventoryLogs
from lifeline.models.product import Product
from lifeline.schemas.inventory_logs import ReasonEnum
from lifeline.services import audit_service


class InsufficientStockError(Exception):
    def __init__(self, product: Product, requested: int, available: int):
        self.product = product
        self.requested = requested
        self.available = available
        super().__init__(
            f"There are only {available} units of {product.product_name} "
            f"recorded in inventory, but {requested} were requested."
        )


def adjust_stock(
    db: Session,
    product: Product,
    quantity_changed: int,
    reason: ReasonEnum,
    user_id=None,
    note: str | None = None,
    allow_negative_stock: bool = False,
    commit: bool = True,
) -> InventoryLogs:

    previous_quantity = product.current_stock
    new_quantity = previous_quantity + quantity_changed

    if new_quantity < 0 and not allow_negative_stock:
        raise InsufficientStockError(
            product, requested=abs(quantity_changed), available=previous_quantity
        )

    product.current_stock = new_quantity

    log = InventoryLogs(
        product_id=product.product_id,
        quantity_changed=quantity_changed,
        previous_quantity=previous_quantity,
        new_quantity=new_quantity,
        reason=reason,
        note=note,
        created_by=user_id,
    )
    db.add(log)

    audit_service.log_action(
        db,
        user_id=user_id,
        action="inventory.adjusted",
        entity_type="product",
        entity_id=product.product_id,
        previous_value={"stock": previous_quantity},
        new_value={"stock": new_quantity},
        reason=f"{reason.value}: {note}" if note else reason.value,
        commit=False,
    )

    if commit:
        db.commit()
        db.refresh(product)
        db.refresh(log)
    return log
