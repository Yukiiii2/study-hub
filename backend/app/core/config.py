from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    cors_origins: str = ""
    supabase_url: str = ""
    supabase_secret_key: SecretStr = SecretStr("")
    database_url: SecretStr = SecretStr("")

    @field_validator("supabase_secret_key")
    @classmethod
    def validate_secret_key(cls, value: SecretStr) -> SecretStr:
        key = value.get_secret_value()
        if key and not key.startswith("sb_secret_"):
            raise ValueError("SUPABASE_SECRET_KEY must be a current Supabase secret key")
        return value

    @field_validator("cors_origins")
    @classmethod
    def validate_origins(cls, value: str) -> str:
        if "*" in value:
            raise ValueError("CORS_ORIGINS must list explicit origins, not wildcards")
        return value

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
