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

    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if not settings.debug and settings.jwt_secret == "PLACEHOLDER":
        raise RuntimeError(
            "JWT_SECRET must be set to a real secret when DEBUG is disabled"
        )
    return settings


settings = get_settings()
