from sqlalchemy import inspect


def test_alembic_migration_creates_initial_tables(migrated_engine) -> None:
    inspector = inspect(migrated_engine)

    assert {
        "users",
        "workspaces",
        "companies",
        "roles",
        "job_sources",
        "stride_evaluations",
        "resume_sources",
        "resume_source_versions",
        "applications",
        "application_state_history",
        "application_notes",
        "application_reminders",
        "application_interview_stages",
        "application_external_links",
        "generated_artifacts",
        "activity_log",
    }.issubset(set(inspector.get_table_names()))

    role_columns = {column["name"] for column in inspector.get_columns("roles")}
    assert {
        "workspace_id",
        "source_id",
        "job_url",
        "remote_type",
        "compensation_min",
        "compensation_max",
        "compensation_currency",
        "raw_description",
        "normalized_description",
        "parse_metadata",
        "status",
        "date_found",
        "date_posted",
    }.issubset(role_columns)

    stride_columns = {
        column["name"] for column in inspector.get_columns("stride_evaluations")
    }
    assert {
        "workspace_id",
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
        "model_used",
        "prompt_version",
        "ruleset_version",
        "input_token_estimate",
        "output_token_estimate",
        "latency_ms",
        "ai_enabled",
        "ai_status",
        "error_message",
        "role_content_hash",
        "source_hash",
        "evaluation_input_hash",
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
        "ix_stride_evaluations_role_input_hash",
        "ix_stride_evaluations_ai_status",
        "ix_stride_evaluations_ruleset_version",
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

    workspace_columns = {column["name"] for column in inspector.get_columns("workspaces")}
    assert {
        "id",
        "user_id",
        "title",
        "description",
        "workspace_type",
        "status",
        "preferences",
        "ai_context_summary",
        "tags",
        "metadata",
        "archived_at",
        "created_at",
        "updated_at",
    }.issubset(workspace_columns)

    generated_artifact_columns = {
        column["name"] for column in inspector.get_columns("generated_artifacts")
    }
    assert "workspace_id" in generated_artifact_columns

    application_columns = {
        column["name"] for column in inspector.get_columns("applications")
    }
    assert {
        "workspace_id",
        "current_state",
        "applied_at",
        "next_action_at",
        "archived_at",
        "reactivated_at",
        "workflow_metadata",
    }.issubset(application_columns)

    application_indexes = {
        index["name"] for index in inspector.get_indexes("applications")
    }
    assert {
        "ix_applications_workspace_id",
        "ix_applications_role_id",
        "ix_applications_current_state",
        "ix_applications_workspace_state",
        "ix_applications_next_action_at",
        "ix_applications_archived_at",
        "uq_applications_active_role_id",
    }.issubset(application_indexes)

    for table_name in (
        "application_state_history",
        "application_notes",
        "application_reminders",
        "application_interview_stages",
        "application_external_links",
    ):
        columns = {column["name"] for column in inspector.get_columns(table_name)}
        assert {"id", "application_id", "user_id", "workspace_id"}.issubset(columns)

    role_indexes = {index["name"] for index in inspector.get_indexes("roles")}
    generated_artifact_indexes = {
        index["name"] for index in inspector.get_indexes("generated_artifacts")
    }
    application_note_columns = {
        column["name"] for column in inspector.get_columns("application_notes")
    }
    application_external_link_columns = {
        column["name"]
        for column in inspector.get_columns("application_external_links")
    }
    application_note_indexes = {
        index["name"] for index in inspector.get_indexes("application_notes")
    }
    application_external_link_indexes = {
        index["name"]
        for index in inspector.get_indexes("application_external_links")
    }
    assert "ix_roles_workspace_id" in role_indexes
    assert "ix_stride_evaluations_workspace_id" in stride_indexes
    assert "ix_generated_artifacts_workspace_id" in generated_artifact_indexes
    assert {"note_type", "deleted_at"}.issubset(application_note_columns)
    assert "deleted_at" in application_external_link_columns
    assert {
        "ix_application_notes_deleted_at",
        "ix_application_notes_note_type",
    }.issubset(application_note_indexes)
    assert (
        "ix_application_external_links_deleted_at"
        in application_external_link_indexes
    )
