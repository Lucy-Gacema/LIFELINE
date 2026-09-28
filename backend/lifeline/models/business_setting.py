from sqlalchemy import Column, String, JSON
from database import Base
from lifeline.models.types import GUID, new_uuid


class BusinessSetting(Base):
   
    __tablename__ = "business_settings"

    key = Column(String, primary_key=True)
    value = Column(JSON, nullable=True)
