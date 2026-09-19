from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, BeforeValidator
from typing import Annotated, List, Any

def split_comma_origins(value: Any) -> List[str]:
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return value

CommaSeparatedOrigins = Annotated[List[str], BeforeValidator(split_comma_origins)]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" 
    )


    ADMIN_EMAIL: EmailStr
    ADMIN_PASSWORD: str
    API_URL: str
    LOGIN_URL: str
    DATABASE_URL: str

 
    SECRET_KEY: str
    ALGORITHM: str = "HS256" 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    ALLOWED_ORIGINS: CommaSeparatedOrigins = ["http://localhost:3000"]


settings = Settings()
