from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from sqlalchemy.exc import IntegrityError
from lifeline.models.sales import Sale
from lifeline.repositories.sales import sale_repository
from lifeline.repositories.products import product_repository
from lifeline.exceptions import EntityNotFoundException, DatabaseOperationException


class SaleService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = sale_repository
        self.product_repo = product_repository

    def create_sale(self, sale_data: dict) -> Sale:
        product = self.product_repo.get(self.db, id=sale_data["product_id"])
        if not product:
            raise EntityNotFoundException(entity_name="Product", identifier=str(sale_data["product_id"]))

        if product.current_stock < sale_data["quantity_sold"]:
            raise DatabaseOperationException(
                action="create",
                entity_name="Sale",
                reason=f"Insufficient inventory. Requested: {sale_data['quantity_sold']}, Available: {product.current_stock}"
            )

        try:
            product.current_stock -= sale_data["quantity_sold"]
            sale_data["total_amount"] = product.selling_price * sale_data["quantity_sold"]
            new_sale = self.repository.create(self.db, data=sale_data)
            return new_sale

        except IntegrityError:
            self.db.rollback()
            raise DatabaseOperationException(
                action="create",
                entity_name="Sale",
                reason="Invalid payload constraints or foreign key conflict."
            )

    def get_sale(self, sale_id: UUID) -> Sale:
        sale = self.repository.get(self.db, sale_id)
        if not sale:
            raise EntityNotFoundException(entity_name="Sale", identifier=str(sale_id))
        return sale

    def update_sale(self, sale_id: UUID, update_data: dict) -> Sale:
        existing_sale = self.get_sale(sale_id)
        try:
            return self.repository.update(self.db, update_data, existing_sale)
        except IntegrityError:
            raise DatabaseOperationException(
                action="update",
                entity_name="Sale",
                reason="Invalid payload attributes."
            )

    def delete_sale(self, sale_id: UUID) -> None:
        existing_sale = self.get_sale(sale_id)
        self.repository.delete(self.db, existing_sale)


    def get_sale(self, sale_id: UUID) -> Sale:
        sale = self.repository.get(self.db, sale_id)
        if not sale:
            raise EntityNotFoundException(entity_name="Sale", identifier=str(sale_id))
        return sale

    def get_all_sales(self) -> List[Sale]:
        return self.repository.get_all(self.db)

    def update_sale(self, sale_id: UUID, update_data: dict) -> Sale:
        existing_sale = self.get_sale(sale_id)
        
        product_id = update_data.get("product_id", existing_sale.product_id)
        product = self.product_repo.get(self.db, id=product_id)
        if not product:
            raise EntityNotFoundException(entity_name="Product", identifier=str(product_id))

        old_quantity = existing_sale.quantity_sold
        new_quantity = update_data.get("quantity_sold", old_quantity)

        if "quantity_sold" in update_data or "product_id" in update_data:
            available_stock_pool = product.current_stock + old_quantity
            if available_stock_pool < new_quantity:
                raise DatabaseOperationException(
                    action="update",
                    entity_name="Sale",
                    reason=f"Insufficient inventory. Required: {new_quantity}, Available: {available_stock_pool}"
                )
            
            product.current_stock = available_stock_pool - new_quantity

        update_data["total_amount"] = product.selling_price * new_quantity

        try:
            return self.repository.update(self.db, update_data, existing_sale)
        except Exception as e:
            raise DatabaseOperationException(
                action="update",
                entity_name="Sale",
                reason=f"Update action failed: {str(e)}"
            )


    def delete_sale(self, sale_id: UUID) -> None:
        existing_sale = self.get_sale(sale_id)
        self.repository.delete(self.db, existing_sale)
