import enum
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
    pin: str | None = Field(None, min_length=4, max_length=6)


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    role: UserEnum | None = None
    is_active: bool | None = None
    custom_permissions: dict | None = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    user_id: uuid.UUID
    is_active: bool
    permissions: list[str] = []


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
