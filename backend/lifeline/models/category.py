from sqlalchemy import Column, String
from database import Base
from lifeline.models.types import GUID, new_uuid


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(GUID(), primary_key=True, default=new_uuid)
    name = Column(String, nullable=False, unique=True)
    icon = Column(String, nullable=True) 
