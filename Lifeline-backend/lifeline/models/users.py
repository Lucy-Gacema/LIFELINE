import uuid
from sqlalchemy.dialects.postgresql import UUID
from lifeline.schemas.users import UserEnum
from database import  Base
from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    Enum,
    String
)

class User(Base):

    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(Enum(UserEnum,native_enum = True ), nullable=False, default="User")
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)







