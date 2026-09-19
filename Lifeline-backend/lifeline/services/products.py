from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from typing import List
from sqlalchemy.exc import IntegrityError
from lifeline.models.products import Product
from lifeline.repositories.products import product_repository
from lifeline.exceptions import EntityNotFoundException, DatabaseOperationException

class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = product_repository

    def create_product(self, product_data: dict) -> Product:
        try:
            return self.repository.create(self.db, product_data)
        except IntegrityError:
            raise DatabaseOperationException(
                action="create",
                entity_name="Product",
                reason="Product already exists"
            )

    def get_all_products(self) -> List[Product]:
        return self.repository.get_all(self.db)

    def get_product(self, product_id: UUID) -> Product:
        product = self.repository.get(self.db, id=product_id)
        if not product:
            raise EntityNotFoundException(entity_name="Product", identifier=str(product_id))
        return product

    def update_product(self, product_id: UUID, update_data: dict) -> Product:
        
        existing_product = self.get_product(product_id)
        try:
            return self.repository.update(self.db, update_data, db_obj=existing_product)
        except IntegrityError:
            raise DatabaseOperationException(
                action="update",
                entity_name="Product",
                reason="Failed to update the product"
            )

    def delete_product(self, product_id: UUID) -> None:
        existing_product = self.get_product(product_id)
        self.repository.delete(self.db, db_obj=existing_product)


    def get_product_name(self, product_id: UUID) -> str:
        product = self.repository.get_product_by_id(self.db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product.product_name 
