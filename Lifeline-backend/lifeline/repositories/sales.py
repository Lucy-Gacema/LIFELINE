from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from lifeline.models.sales import Sale

class SaleRepository:
    def __init__(self):
        self.model = Sale

    def get(self, db: Session, id: UUID):
        return db.query(self.model).options(
            joinedload(self.model.product)
        ).filter(self.model.sale_id == id).first()

    def get_all(self, db: Session):
        return db.query(self.model).options(
            joinedload(self.model.product)
        ).all()

    def create(self, db: Session, data: dict):
        try:
            sale = self.model(**data)
            db.add(sale)
            db.commit()
            db.refresh(sale)
            return sale
        except Exception:
            db.rollback()  # Protect session health state
            raise


    def update(self, db: Session, data: dict, db_obj: Sale):
        try:
            for field, value in data.items():
                setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception:
            db.rollback()
            raise

    def delete(self, db: Session, db_obj: Sale) -> None:
        try:
            db.delete(db_obj)
            db.commit()
        except Exception:
            db.rollback()
            raise

sale_repository = SaleRepository()
