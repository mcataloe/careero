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

    role_columns = {column["name"] for column in inspector.get_columns("roles")}
    assert {
        "source_id",
        "job_url",
        "remote_type",
        "compensation_min",
        "compensation_max",
        "compensation_currency",
        "raw_description",
        "normalized_description",
        "status",
        "date_found",
        "date_posted",
    }.issubset(role_columns)
