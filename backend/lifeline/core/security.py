from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from lifeline.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_secret(raw: str) -> str:

    return pwd_context.hash(raw)


def verify_secret(raw: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(raw, hashed)
    except Exception:
        return False


def create_access_token(data: dict, expires_minutes: int | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
