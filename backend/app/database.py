from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings, get_settings


def sqlalchemy_url(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def create_database_engine(settings: Settings | None = None) -> Engine:
    settings = settings or get_settings()
    return create_engine(
        sqlalchemy_url(settings.database_url),
        connect_args={"connect_timeout": 3},
        pool_pre_ping=True,
    )


engine = create_database_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database(settings: Settings | None = None) -> None:
    database_engine = create_database_engine(settings)
    try:
        with database_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    finally:
        database_engine.dispose()
