import os
from pathlib import Path
from typing import List

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _split_csv(value: str) -> List[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


class Settings:
    APP_NAME: str = "LIFELINE POS"
    ENV: str = os.getenv("ENV", "development")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{Path(__file__).resolve().parents[3] / 'lifeline.db'}"
    )

    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION_ENV_FILE")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
    PIN_SESSION_EXPIRE_MINUTES: int = int(os.getenv("PIN_SESSION_EXPIRE_MINUTES", "480"))
    IDLE_TIMEOUT_MINUTES: int = int(os.getenv("IDLE_TIMEOUT_MINUTES", "15"))

    ALLOWED_ORIGINS: List[str] = _split_csv(
        os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    )

    DEFAULT_CURRENCY: str = os.getenv("DEFAULT_CURRENCY", "KES")
    DEFAULT_LOW_STOCK_THRESHOLD: int = int(os.getenv("DEFAULT_LOW_STOCK_THRESHOLD", "5"))
    ALLOW_NEGATIVE_STOCK_DEFAULT: bool = os.getenv("ALLOW_NEGATIVE_STOCK_DEFAULT", "false").lower() == "true"

    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "google")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gemini-3.8-flash")

    SYNC_BATCH_SIZE: int = int(os.getenv("SYNC_BATCH_SIZE", "100"))


settings = Settings()
