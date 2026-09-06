from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Weekly Report API"

    app_env: Literal[
        "local",
        "development",
        "testing",
        "staging",
        "production",
    ] = "local"

    app_debug: bool = False

    api_v1_prefix: str = "/api/v1"

    cors_origins: list[str] = [
        "http://localhost:5173",
    ]

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_database: str = "weekly_report"
    mysql_user: str = "root"
    mysql_password: str = Field(repr=False)

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()