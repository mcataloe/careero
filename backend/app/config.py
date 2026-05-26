from functools import lru_cache
from typing import ClassVar

from pydantic import Field, field_validator, model_validator
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
    enable_ai_evaluations: bool = Field(default=False)
    enable_ai_role_parsing: bool = Field(default=False)
    enable_ai_resume_generation: bool = Field(default=False)
    enable_ai_cover_letter_generation: bool = Field(default=False)
    openai_api_key: str = Field(default="")
    openai_default_evaluation_model: str = Field(default="gpt-5-mini")
    openai_default_role_parsing_model: str = Field(default="gpt-5-mini")
    openai_default_resume_generation_model: str = Field(default="gpt-5-mini")
    openai_default_cover_letter_generation_model: str = Field(default="gpt-5-mini")
    openai_timeout_seconds: int = Field(default=30)
    openai_max_output_tokens: int = Field(default=2500)
    max_ai_evaluations_per_session: int = Field(default=25)
    log_level: str = Field(default="INFO")
    auth_session_cookie_name: str = Field(default="careero_session")
    auth_session_days: int = Field(default=14)
    auth_cookie_secure: bool = Field(default=False)
    enable_password_auth: bool = Field(default=True)
    allow_registration: bool = Field(default=True)
    password_min_length: int = Field(default=12)

    @field_validator(
        "app_name",
        "environment",
        "database_url",
        "test_database_url",
        "openai_default_evaluation_model",
        "openai_default_role_parsing_model",
        "openai_default_resume_generation_model",
        "openai_default_cover_letter_generation_model",
        "log_level",
        "auth_session_cookie_name",
    )
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must not be blank")
        return value.strip()

    @field_validator("openai_timeout_seconds")
    @classmethod
    def openai_timeout_must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("must be greater than zero")
        return value

    @field_validator("openai_max_output_tokens")
    @classmethod
    def openai_max_output_tokens_must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("must be greater than zero")
        return value

    @field_validator("max_ai_evaluations_per_session")
    @classmethod
    def max_ai_evaluations_per_session_must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("must be greater than zero")
        return value

    @field_validator("auth_session_days")
    @classmethod
    def auth_session_days_must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("must be greater than zero")
        return value

    @field_validator("password_min_length")
    @classmethod
    def password_min_length_must_be_reasonable(cls, value: int) -> int:
        if value < 8:
            raise ValueError("must be at least 8")
        return value

    @model_validator(mode="after")
    def openai_key_can_be_blank_for_fallback(self) -> "Settings":
        self.openai_api_key = self.openai_api_key.strip()
        return self

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
