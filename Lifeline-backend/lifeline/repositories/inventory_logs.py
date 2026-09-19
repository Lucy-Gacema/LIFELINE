from sqlalchemy.orm import Session, joinedload
import uuid as UUID
from lifeline.models.inventory_logs import InventoryLogs

class InventoryLogRepository:
    def __init__(self):
        self.model = InventoryLogs

    def get(self, db:Session, id:UUID):
        return db.query(self.model).options(
            joinedload(self.model.product)
        ).filter(self.model.inventory_logs_id==id).first() 

    def get_all(self, db:Session):
        return db.query(self.model).options(
            joinedload(self.model.product)
        ).filter(self.model.product).all()
    
    def create(self, db:Session, data:dict):
        inventory_log = self.model(**data)
        db.add(inventory_log)
        db.commit()
        db.refresh(inventory_log)
        return inventory_log

    def update(self, db:Session, data:dict, db_obj:InventoryLogs):
        for field , value in data.items():
            setattr (db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        

inventory_logs_repository = InventoryLogRepository()


