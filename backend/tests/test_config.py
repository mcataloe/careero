import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()


def test_settings_accept_empty_openai_api_key() -> None:
    settings = Settings(_env_file=None, openai_api_key="")

    assert settings.openai_api_key == ""


def test_settings_have_safe_local_defaults_without_env_file() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_name == "Careero API"
    assert settings.environment == "local"
    assert settings.database_url == "postgresql://careero:careero@localhost:5432/careero"
    assert (
        settings.test_database_url
        == "postgresql://careero:careero@localhost:5432/careero_test"
    )
    assert settings.log_level == "INFO"


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("app_name", ""),
        ("environment", " "),
        ("database_url", ""),
        ("test_database_url", ""),
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
