from sqlalchemy import inspect


def test_alembic_migration_creates_initial_tables(migrated_engine) -> None:
    inspector = inspect(migrated_engine)

    assert {
        "users",
        "companies",
        "roles",
        "job_sources",
        "stride_evaluations",
        "applications",
        "generated_artifacts",
        "activity_log",
    }.issubset(set(inspector.get_table_names()))
