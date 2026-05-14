import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()


def test_settings_accept_empty_openai_api_key() -> None:
    settings = Settings(_env_file=None, openai_api_key="")

    assert settings.openai_api_key == ""


def test_settings_have_safe_local_defaults_without_env_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CAREERO_DATABASE_URL", raising=False)
    monkeypatch.delenv("CAREERO_TEST_DATABASE_URL", raising=False)
    settings = Settings(_env_file=None)

    assert settings.app_name == "Careero API"
    assert settings.environment == "local"
    assert settings.database_url == "postgresql://careero:careero@localhost:5432/careero"
    assert (
        settings.test_database_url
        == "postgresql://careero:careero@localhost:5432/careero_test"
    )
    assert settings.enable_ai_evaluations is False
    assert settings.enable_ai_role_parsing is False
    assert settings.enable_ai_resume_generation is False
    assert settings.enable_ai_cover_letter_generation is False
    assert settings.openai_default_evaluation_model == "gpt-5-mini"
    assert settings.openai_default_role_parsing_model == "gpt-5-mini"
    assert settings.openai_default_resume_generation_model == "gpt-5-mini"
    assert settings.openai_default_cover_letter_generation_model == "gpt-5-mini"
    assert settings.openai_timeout_seconds == 30
    assert settings.openai_max_output_tokens == 2500
    assert settings.max_ai_evaluations_per_session == 25
    assert settings.log_level == "INFO"


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("app_name", ""),
        ("environment", " "),
        ("database_url", ""),
        ("test_database_url", ""),
        ("openai_default_evaluation_model", ""),
        ("openai_default_role_parsing_model", ""),
        ("openai_default_resume_generation_model", ""),
        ("openai_default_cover_letter_generation_model", ""),
        ("log_level", ""),
    ],
)
def test_settings_reject_blank_required_values(field_name: str, value: str) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **{field_name: value})


def test_settings_reject_invalid_log_level() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, log_level="LOUD")


def test_settings_normalize_log_level() -> None:
    settings = Settings(_env_file=None, log_level="debug")

    assert settings.log_level == "DEBUG"


def test_settings_accept_ai_enabled_with_valid_openai_options() -> None:
    settings = Settings(
        _env_file=None,
        enable_ai_evaluations=True,
        enable_ai_role_parsing=True,
        enable_ai_resume_generation=True,
        enable_ai_cover_letter_generation=True,
        openai_api_key=" sk-test ",
        openai_default_evaluation_model="gpt-5-mini",
        openai_default_role_parsing_model="gpt-5-mini",
        openai_default_resume_generation_model="gpt-5-mini",
        openai_default_cover_letter_generation_model="gpt-5-mini",
        openai_timeout_seconds=45,
        openai_max_output_tokens=3000,
        max_ai_evaluations_per_session=10,
    )

    assert settings.enable_ai_evaluations is True
    assert settings.enable_ai_role_parsing is True
    assert settings.enable_ai_resume_generation is True
    assert settings.enable_ai_cover_letter_generation is True
    assert settings.openai_api_key == "sk-test"
    assert settings.openai_default_role_parsing_model == "gpt-5-mini"
    assert settings.openai_default_resume_generation_model == "gpt-5-mini"
    assert settings.openai_default_cover_letter_generation_model == "gpt-5-mini"
    assert settings.openai_timeout_seconds == 45
    assert settings.openai_max_output_tokens == 3000
    assert settings.max_ai_evaluations_per_session == 10


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("openai_timeout_seconds", 0),
        ("openai_timeout_seconds", -1),
        ("openai_max_output_tokens", 0),
        ("openai_max_output_tokens", -10),
        ("max_ai_evaluations_per_session", 0),
        ("max_ai_evaluations_per_session", -1),
    ],
)
def test_settings_reject_invalid_openai_numeric_options(
    field_name: str,
    value: int,
) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **{field_name: value})
