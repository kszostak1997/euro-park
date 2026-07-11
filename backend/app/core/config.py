from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "Euro Park API"
    debug: bool = True

    database_url: str = "sqlite+aiosqlite:///./euro_park.db"

    jwt_secret: str = "PLACEHOLDER"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    admin_email: str = "admin@eurocert.com"
    admin_password: str = "admin"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
