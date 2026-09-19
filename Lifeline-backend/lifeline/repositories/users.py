from sqlalchemy.orm import Session
from lifeline.models.users import User
from uuid import UUID

class UserRepository:
    def __init__(self):
        self.model= User

    def get(self, db:Session, id:UUID):
        return db.query(self.model).filter(self.model.user_id == id).first()

    def get_all(self, db:Session):
        users = db.query(self.model).all()
        return users

    def create (self, db:Session,data:dict):
        user = self.model(**data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(self, db:Session, data:dict, db_obj:User):
        for field, value in data.items():
            setattr (db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def delete (self, db:Session, db_obj:User):
        db.delete(db_obj)
        db.commit()


    def get_user_by_email(self, db:Session, email:str):
        return db.query(User).filter(User.email==email).first()


user_repository = UserRepository()
