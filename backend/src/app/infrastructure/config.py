from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    app_name: str = Field(default="Affordable API", validation_alias="APP_NAME")
    app_env: Literal["development", "test", "staging", "production"] = Field(
        default="development",
        validation_alias="APP_ENV",
    )
    debug: bool = Field(default=False, validation_alias="APP_DEBUG")
    api_v1_prefix: str = Field(default="/api/v1", validation_alias="APP_API_V1_PREFIX")
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        validation_alias="APP_CORS_ORIGINS",
    )
    database_url: str = Field(
        default="postgresql+asyncpg://affordable:affordable@localhost:5432/affordable",
        validation_alias="APP_DATABASE_URL",
    )
    jwt_secret: str = Field(
        min_length=32,
        validation_alias="APP_JWT_SECRET",
    )
    jwt_issuer: str = Field(default="affordable-api", validation_alias="APP_JWT_ISSUER")
    jwt_audience: str = Field(default="affordable-client", validation_alias="APP_JWT_AUDIENCE")
    access_token_ttl_minutes: int = Field(
        default=15,
        ge=1,
        le=60,
        validation_alias="APP_ACCESS_TOKEN_TTL_MINUTES",
    )
    refresh_token_ttl_days: int = Field(
        default=30,
        ge=1,
        le=90,
        validation_alias="APP_REFRESH_TOKEN_TTL_DAYS",
    )
    bootstrap_admin_email: str | None = Field(
        default=None,
        validation_alias="APP_BOOTSTRAP_ADMIN_EMAIL",
    )
    bootstrap_admin_password: str | None = Field(
        default=None,
        validation_alias="APP_BOOTSTRAP_ADMIN_PASSWORD",
    )
    auto_create_schema: bool = Field(
        default=False,
        validation_alias="APP_AUTO_CREATE_SCHEMA",
    )

    @model_validator(mode="after")
    def validate_security_and_database(self) -> "Settings":
        if self.app_env != "test" and not self.database_url.startswith("postgresql+asyncpg://"):
            raise ValueError("Вне тестов APP_DATABASE_URL должен использовать PostgreSQL + asyncpg")
        admin_values = (self.bootstrap_admin_email, self.bootstrap_admin_password)
        if any(admin_values) and not all(admin_values):
            raise ValueError("Для bootstrap-администратора нужны одновременно email и password")
        if self.bootstrap_admin_password and len(self.bootstrap_admin_password) < 12:
            raise ValueError("Пароль bootstrap-администратора должен быть не короче 12 символов")
        insecure_prefixes = ("replace-with", "development-secret")
        if self.app_env in {"staging", "production"} and self.jwt_secret.startswith(
            insecure_prefixes
        ):
            raise ValueError("В staging/production необходимо заменить APP_JWT_SECRET")
        if self.app_env in {"staging", "production"} and self.debug:
            raise ValueError("APP_DEBUG должен быть выключен в staging/production")
        if "*" in self.cors_origins:
            raise ValueError("Wildcard CORS несовместим с credential-запросами")
        if not self.api_v1_prefix.startswith("/"):
            raise ValueError("APP_API_V1_PREFIX должен начинаться с /")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
