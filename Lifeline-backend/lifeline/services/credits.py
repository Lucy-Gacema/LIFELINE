from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from lifeline.exceptions import EntityNotFoundException, DatabaseOperationException
from lifeline.models .sales import Sale
from lifeline.models.credits import Credit
from lifeline.repositories.credits import credit_repository

class CreditService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = credit_repository
        self.model = Credit

    def create_credit(self, credit_data: dict) -> Credit:
        try:
            if "is_paid" not in credit_data:
                credit_data["is_paid"] = False

            new_credit = self.repository.create(self.db, data=credit_data)
            self.db.commit() 
            return new_credit
        except IntegrityError as e:
            self.db.rollback() 
            raise DatabaseOperationException(
                action="create",
                entity_name="Credit",
                reason="The referenced sale does not match inventory logs"
            )
        except Exception:
            self.db.rollback()
            raise

    def get_all_credit(self, db: Session):
        return db.query(self.model).options(
            joinedload(self.model.sale).joinedload(Sale.product)  
        ).all()

    def get(self, db: Session, id: UUID):
        return db.query(self.model).options(
            joinedload(self.model.sale).joinedload(Sale.product)  
        ).filter(self.model.credit_id == id).first()
        
    def update_credit(self, credit_id: UUID, update_data: dict) -> Credit:
        existing_credit = self.get(self.db, credit_id) 
        if not existing_credit:
            raise EntityNotFoundException(entity_name="Credit", entity_id=credit_id)
        try:
            updated_credit = self.repository.update(self.db, data=update_data, db_obj=existing_credit)
            self.db.commit() 
            return updated_credit
        except IntegrityError:
            self.db.rollback()
            raise DatabaseOperationException(
                action="update", 
                entity_name="Credit", 
                reason="Invalid payload attributes or foreign key constraint conflict detected."
            )
        except Exception:
            self.db.rollback()
            raise

    def delete_credit(self, credit_id: UUID) -> None:
        existing_credit = self.get(self.db, credit_id)
        if not existing_credit:
            raise EntityNotFoundException(entity_name="Credit", entity_id=credit_id)

        try:
            self.repository.delete(self.db, db_obj=existing_credit)
            self.db.commit() 
        except Exception:
            self.db.rollback()
            raise
