from sqlalchemy import inspect


def test_alembic_migration_creates_initial_tables(migrated_engine) -> None:
    inspector = inspect(migrated_engine)

    assert {
        "users",
        "companies",
        "roles",
        "job_sources",
        "stride_evaluations",
        "resume_sources",
        "resume_source_versions",
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

    stride_columns = {
        column["name"] for column in inspector.get_columns("stride_evaluations")
    }
    assert {
        "evaluation_status",
        "overall_score",
        "recommendation",
        "confidence_level",
        "summary",
        "strengths",
        "concerns",
        "resume_alignment",
        "compensation_alignment",
        "seniority_alignment",
        "remote_alignment",
        "technical_alignment",
        "company_risk",
        "ats_keywords",
        "missing_keywords",
        "raw_evaluation_json",
        "created_at",
        "updated_at",
        "deleted_at",
    }.issubset(stride_columns)

    stride_indexes = {
        index["name"] for index in inspector.get_indexes("stride_evaluations")
    }
    assert {
        "ix_stride_evaluations_user_id",
        "ix_stride_evaluations_role_id",
        "ix_stride_evaluations_status",
        "ix_stride_evaluations_role_created_at",
    }.issubset(stride_indexes)

    resume_source_columns = {
        column["name"] for column in inspector.get_columns("resume_sources")
    }
    assert {
        "id",
        "user_id",
        "name",
        "source_type",
        "created_at",
        "updated_at",
    }.issubset(resume_source_columns)

    resume_source_version_columns = {
        column["name"] for column in inspector.get_columns("resume_source_versions")
    }
    assert {
        "id",
        "user_id",
        "source_id",
        "version_label",
        "raw_text",
        "normalized_summary",
        "is_active",
        "created_at",
        "updated_at",
    }.issubset(resume_source_version_columns)

    resume_source_version_indexes = {
        index["name"] for index in inspector.get_indexes("resume_source_versions")
    }
    assert "uq_resume_source_versions_active_user" in resume_source_version_indexes
