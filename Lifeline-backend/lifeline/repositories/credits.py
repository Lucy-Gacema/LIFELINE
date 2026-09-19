from sqlalchemy.orm import Session, joinedload
from lifeline.models.credits import Credit
from uuid import UUID

class CreditRepository:
    def __init__(self):
        self.model = Credit

    def get(self, db:Session, id:UUID):
        return db.query(self.model).options(
            joinedload(self.model.sale).joinedload(self.model.sale.product)
        ).filter(self.model.credit_id==id).first()
    

    def get_all(self, db:Session):
        return db.query(self.model).options(
            joinedload(self.model.sale).joinedload(self.model.sale.product)
        ).all()
        

    def create(self, db:Session,data:dict):
        credit = self.model(**data)
        db.add(credit)
        db.commit()
        db.refresh(credit)
        return credit

    def update(self, db:Session, data:dict, db_obj:Credit):
        for field, value in data.items():
            setattr(db_obj, field,value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db:Session, db_obj:Credit):
        db.delete(db_obj)
        db.commit()

credit_repository = CreditRepository()




    