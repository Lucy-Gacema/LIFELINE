from typing import Any, List
from uuid import UUID
from sqlalchemy.orm import Session
from lifeline.models import Product
from lifeline.models.inventory_logs import InventoryLogs 
from lifeline.repositories.inventory_logs import inventory_logs_repository
from lifeline.repositories.products import product_repository
from lifeline.exceptions import EntityNotFoundException, DatabaseOperationException

class InventoryLogService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = inventory_logs_repository
        self.product_repo = product_repository

    def _get_stock_delta(self, reason: Any, quantity: int) -> int:
        if not reason:
            return 0
            
        reason_str = reason.value if hasattr(reason, 'value') else str(reason)
        reason_normalized = reason_str.strip().lower()
    
        if reason_normalized == "restock":
            return quantity
        if reason_normalized in ["damaged", "expired"]:
            return -quantity
        return 0

    def create_log(self, log_data: dict) -> InventoryLogs:
        product = (
            self.db.query(Product)
            .filter(Product.product_id == log_data["product_id"])
            .with_for_update()
            .first()
        ) 
        if not product:
            raise EntityNotFoundException(
                entity_name="Product", 
                identifier=str(log_data["product_id"])
            )
        
        delta = self._get_stock_delta(log_data["reason"], log_data["quantity_changed"])

        product.current_stock += delta
        try:
            self.db.add(product)
            new_log = self.repository.create(self.db, data=log_data)
            self.db.commit()  
            self.db.refresh(product)           
            self.db.refresh(new_log)
            return new_log
            
        except Exception as e:
            self.db.rollback() 
            print(f"[DEBUG - ERROR] Transaction failed! Rolling back. Error details: {str(e)}")
            raise DatabaseOperationException(
                action="create",
                entity_name="Inventory Log",
                reason=f"Failed transaction context: {str(e)}"
            )

    def update_log(self, log_id: UUID, update_data: dict) -> InventoryLogs:
        existing_log = self.repository.get(self.db, id=log_id)
        if not existing_log:
            raise EntityNotFoundException(entity_name="Inventory Log", identifier=str(log_id))
        
        product = (
            self.db.query(Product)
            .filter(Product.product_id == existing_log.product_id)
            .with_for_update()
            .first()
        )
        if not product:
            raise EntityNotFoundException(entity_name="Product", identifier=str(existing_log.product_id))

        try:
            old_delta = self._get_stock_delta(existing_log.reason, existing_log.quantity_changed)
            product.current_stock -= old_delta 
            raw_reason = update_data.get("reason") if "reason" in update_data else existing_log.reason
            raw_quantity = update_data.get("quantity_changed") if "quantity_changed" in update_data else existing_log.quantity_changed

            new_delta = self._get_stock_delta(raw_reason, int(raw_quantity))
            product.current_stock += new_delta
            self.db.add(product)

            updated_log = self.repository.update(self.db, data=update_data, db_obj=existing_log)
            self.db.commit()
            
            return updated_log
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseOperationException(
                action="update",
                entity_name="Inventory Log",
                reason=f"Failed to execute update calculation : {str(e)}"
            )

    def get_all_logs(self) -> List[InventoryLogs]:
        return self.repository.get_all(self.db) 


    def get_log(self, log_id: UUID) -> InventoryLogs:
        log_entry = self.repository.get(self.db, id=log_id)
        if not log_entry:
            raise EntityNotFoundException(
                entity_name="Inventory Log", 
                identifier=str(log_id)
            )
            
        return log_entry
