import enum
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserEnum(str, enum.Enum):
    ADMIN = "Admin"
    MANAGER = "Manager"
    CASHIER = "Cashier"


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: UserEnum = UserEnum.CASHIER


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    pin: Optional[str] = Field(None, min_length=4, max_length=6)


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserEnum] = None
    is_active: Optional[bool] = None
    custom_permissions: Optional[dict] = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    user_id: uuid.UUID
    is_active: bool
    permissions: List[str] = []


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PinLoginRequest(BaseModel):
    user_id: uuid.UUID
    pin: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
