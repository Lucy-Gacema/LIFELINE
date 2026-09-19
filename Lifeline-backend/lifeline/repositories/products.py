from sqlalchemy.orm import Session
from uuid import UUID
from lifeline.models.products import Product

class ProductRepository:
    def __init__(self):
        self.model= Product

    def get(self, db:Session, id:UUID):
        return db.query(self.model).filter(self.model.product_id==id).first()
    

    def get_all(self, db:Session):
         return db.query(self.model).all()

    def create (self, db:Session,data:dict):
        product = self.model(**data)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def update(self, db:Session, data:dict, db_obj:Product):
        for field, value in data.items():
            setattr (db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete (self, db:Session, db_obj:Product):
        db.delete(db_obj)
        db.commit()

    def get_product_by_id(self, db: Session, product_id: UUID):
        return db.query(Product).filter(Product.product_id == product_id).first()



product_repository = ProductRepository()


    
