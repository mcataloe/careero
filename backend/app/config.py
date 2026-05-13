from functools import lru_cache
from typing import ClassVar

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CAREERO_",
        extra="ignore",
    )

    valid_log_levels: ClassVar[set[str]] = {
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    }

    app_name: str = Field(default="Careero API")
    environment: str = Field(default="local")
    database_url: str = Field(
        default="postgresql://careero:careero@localhost:5432/careero"
    )
    test_database_url: str = Field(
        default="postgresql://careero:careero@localhost:5432/careero_test"
    )
    openai_api_key: str = Field(default="")
    log_level: str = Field(default="INFO")

    @field_validator(
        "app_name",
        "environment",
        "database_url",
        "test_database_url",
        "log_level",
    )
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must not be blank")
        return value.strip()

    @field_validator("log_level")
    @classmethod
    def log_level_must_be_valid(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in cls.valid_log_levels:
            raise ValueError(
                "must be one of DEBUG, INFO, WARNING, ERROR, or CRITICAL"
            )
        return normalized


@lru_cache
def get_settings() -> Settings:
    return Settings()
