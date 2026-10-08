from sqlalchemy import JSON, Column, String

from database import Base


class BusinessSetting(Base):
    __tablename__ = "business_settings"

    key = Column(String, primary_key=True)
    value = Column(JSON, nullable=True)
