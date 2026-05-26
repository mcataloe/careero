import os
from collections.abc import Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.database import sqlalchemy_url

BACKEND_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture
def test_database_url() -> str:
    database_url = os.environ.get("CAREERO_TEST_DATABASE_URL")
    if not database_url:
        pytest.fail(
            "CAREERO_TEST_DATABASE_URL is required for database-backed tests. "
            "Create the local PostgreSQL test database documented in backend/README.md."
        )
    return database_url


@pytest.fixture
def alembic_config(monkeypatch: pytest.MonkeyPatch, test_database_url: str) -> Config:
    monkeypatch.setenv("CAREERO_DATABASE_URL", test_database_url)
    get_settings.cache_clear()

    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return config


def drop_known_schema(database_url: str) -> None:
    engine = create_engine(sqlalchemy_url(database_url), isolation_level="AUTOCOMMIT")
    try:
        try:
            with engine.connect() as connection:
                connection.execute(
                    text(
                        """
                        DROP TABLE IF EXISTS
                            automation_approval_logs,
                            automation_suggestions,
                            account_lifecycle_requests,
                            activity_log,
                            artifact_performance_records,
                            generated_artifacts,
                            application_external_links,
                            application_interview_stages,
                            application_reminders,
                            application_notes,
                            application_state_history,
                            applications,
                            compass_evaluations,
                            resume_source_versions,
                            resume_sources,
                            roles,
                            workspaces,
                            job_sources,
                            companies,
                            users,
                            alembic_version
                        CASCADE
                        """
                    )
                )
        except SQLAlchemyError as exc:
            raise RuntimeError(
                "Could not connect to CAREERO_TEST_DATABASE_URL. "
                "Create the documented local PostgreSQL test database and "
                "confirm the URL credentials are correct. "
                f"Error type: {type(exc).__name__}"
            ) from None
    finally:
        engine.dispose()


@pytest.fixture
def migrated_database(
    alembic_config: Config,
    test_database_url: str,
) -> Generator[str, None, None]:
    drop_known_schema(test_database_url)
    command.upgrade(alembic_config, "head")
    yield test_database_url
    drop_known_schema(test_database_url)


@pytest.fixture
def migrated_engine(migrated_database: str) -> Generator[Engine, None, None]:
    engine = create_engine(sqlalchemy_url(migrated_database))
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def db_session(migrated_engine: Engine) -> Generator[Session, None, None]:
    session_factory = sessionmaker(
        bind=migrated_engine,
        autoflush=False,
        autocommit=False,
    )
    with session_factory() as session:
        yield session
