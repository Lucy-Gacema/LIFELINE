from pydantic import BaseModel, field_validator, Field, EmailStr
from sqlalchemy import Enum as SQLEnum
import enum
from uuid import UUID
import re
from typing import Optional

class UserEnum(str, enum.Enum):
    ADMIN = "Admin"
    USER = "User"

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email : EmailStr
    role: UserEnum
  

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length = 36)


    @field_validator("password")
    @classmethod
    def validate_strong_password(cls, value: str) -> str:
        
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_]", value):
            raise ValueError("Password must contain at least one special character.")
        return value

class UserUpdate(BaseModel):
    first_name: Optional[str]=None
    last_name : Optional[str]=None
    email :Optional[str] =None
    password :Optional[ str] =None
    user_type: Optional[UserEnum ]=None

class UserResponse(UserBase):
    user_id : UUID

    class Config:
        from_attributes = True

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    role: str