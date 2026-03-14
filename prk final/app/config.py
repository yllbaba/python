from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str
    db_path: str
    auth_token_ttl_minutes: int
    password_pepper: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Basketball Game Tracker"),
        db_path=os.getenv("DB_PATH", "basketball.db"),
        auth_token_ttl_minutes=int(os.getenv("AUTH_TOKEN_TTL_MINUTES", "1440")),
        password_pepper=os.getenv("PASSWORD_PEPPER", "change-me"),
    )
