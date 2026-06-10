from sqlalchemy import inspect


def test_alembic_migration_creates_initial_tables(migrated_engine) -> None:
    inspector = inspect(migrated_engine)

    assert {
        "users",
        "workspaces",
        "companies",
        "opportunities",
        "job_sources",
        "compass_evaluations",
        "resume_sources",
        "resume_source_versions",
        "applications",
        "application_state_history",
        "application_notes",
        "application_reminders",
        "application_interview_stages",
        "application_external_links",
        "generated_artifacts",
        "automation_suggestions",
        "automation_approval_logs",
        "activity_log",
        "auth_sessions",
    }.issubset(set(inspector.get_table_names()))

    opportunity_columns = {
        column["name"] for column in inspector.get_columns("opportunities")
    }
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
    }.issubset(opportunity_columns)

    compass_columns = {
        column["name"] for column in inspector.get_columns("compass_evaluations")
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
    }.issubset(compass_columns)

    compass_indexes = {
        index["name"] for index in inspector.get_indexes("compass_evaluations")
    }
    assert {
        "ix_compass_evaluations_user_id",
        "ix_compass_evaluations_opportunity_id",
        "ix_compass_evaluations_status",
        "ix_compass_evaluations_opportunity_created_at",
        "ix_compass_evaluations_opportunity_input_hash",
        "ix_compass_evaluations_ai_status",
        "ix_compass_evaluations_ruleset_version",
    }.issubset(compass_indexes)

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
    assert {
        "workspace_id",
        "source_artifact_id",
        "evaluation_id",
        "source_resume_version_id",
        "lifecycle_status",
        "version_number",
        "reviewed_at",
        "submitted_at",
        "archived_at",
    }.issubset(generated_artifact_columns)

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
        "ix_applications_opportunity_id",
        "ix_applications_current_state",
        "ix_applications_workspace_state",
        "ix_applications_next_action_at",
        "ix_applications_archived_at",
        "uq_applications_active_opportunity_id",
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

    opportunity_indexes = {
        index["name"] for index in inspector.get_indexes("opportunities")
    }
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
    assert "ix_opportunities_workspace_id" in opportunity_indexes
    assert "ix_compass_evaluations_workspace_id" in compass_indexes
    assert "ix_generated_artifacts_workspace_id" in generated_artifact_indexes
    assert {
        "ix_generated_artifacts_lifecycle_status",
        "ix_generated_artifacts_evaluation_id",
        "ix_generated_artifacts_source_artifact_id",
    }.issubset(generated_artifact_indexes)
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

    automation_suggestion_columns = {
        column["name"] for column in inspector.get_columns("automation_suggestions")
    }
    assert {
        "id",
        "user_id",
        "workspace_id",
        "target_type",
        "target_id",
        "opportunity_id",
        "application_id",
        "artifact_id",
        "action_type",
        "preview_hash",
        "status",
        "policy_version",
    }.issubset(automation_suggestion_columns)

    automation_approval_columns = {
        column["name"] for column in inspector.get_columns("automation_approval_logs")
    }
    assert {
        "id",
        "user_id",
        "workspace_id",
        "suggestion_id",
        "actor",
        "target_type",
        "target_id",
        "action_type",
        "preview_hash",
        "approval_status",
        "execution_status",
        "external_mutation",
        "policy_version",
    }.issubset(automation_approval_columns)

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    assert {
        "email_normalized",
        "first_name",
        "last_name",
        "salutation",
        "pronouns",
        "headshot_url",
        "password_hash",
        "password_updated_at",
        "last_login_at",
        "auth_method",
        "account_status",
        "failed_login_count",
        "locked_until",
    }.issubset(user_columns)
    assert "username" not in user_columns
    assert "username_normalized" not in user_columns

    auth_session_columns = {
        column["name"] for column in inspector.get_columns("auth_sessions")
    }
    assert {
        "id",
        "user_id",
        "session_token_hash",
        "expires_at",
        "revoked_at",
        "last_seen_at",
        "user_agent",
        "ip_hint",
        "metadata",
        "created_at",
        "updated_at",
    }.issubset(auth_session_columns)
