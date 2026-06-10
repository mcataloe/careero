"""opportunity persistence migration

Revision ID: 0020_opportunity_persistence
Revises: 0019_artifact_lifecycle
Create Date: 2026-06-10
"""

from alembic import op


revision = "0020_opportunity_persistence"
down_revision = "0019_artifact_lifecycle"
branch_labels = None
depends_on = None


ROLE_ID_TABLES = (
    "compass_evaluations",
    "applications",
    "generated_artifacts",
    "artifact_performance_records",
    "automation_suggestions",
    "ai_usage_events",
)


INDEX_RENAMES_UP = (
    ("ix_roles_user_id", "ix_opportunities_user_id"),
    ("ix_roles_workspace_id", "ix_opportunities_workspace_id"),
    ("ix_roles_company_id", "ix_opportunities_company_id"),
    ("ix_roles_source_id", "ix_opportunities_source_id"),
    ("ix_roles_status", "ix_opportunities_status"),
    ("ix_roles_user_status", "ix_opportunities_user_status"),
    ("ix_compass_evaluations_role_id", "ix_compass_evaluations_opportunity_id"),
    (
        "ix_compass_evaluations_role_created_at",
        "ix_compass_evaluations_opportunity_created_at",
    ),
    (
        "ix_compass_evaluations_role_input_hash",
        "ix_compass_evaluations_opportunity_input_hash",
    ),
    ("ix_applications_role_id", "ix_applications_opportunity_id"),
    ("uq_applications_active_role_id", "uq_applications_active_opportunity_id"),
    ("ix_generated_artifacts_role_id", "ix_generated_artifacts_opportunity_id"),
    (
        "ix_artifact_performance_records_role_id",
        "ix_artifact_performance_records_opportunity_id",
    ),
    ("ix_automation_suggestions_role_id", "ix_automation_suggestions_opportunity_id"),
    ("ix_ai_usage_events_role_id", "ix_ai_usage_events_opportunity_id"),
)


def _rename_index(old_name: str, new_name: str) -> None:
    op.execute(f'ALTER INDEX IF EXISTS "{old_name}" RENAME TO "{new_name}"')


def upgrade() -> None:
    op.rename_table("roles", "opportunities")
    for table_name in ROLE_ID_TABLES:
        op.alter_column(table_name, "role_id", new_column_name="opportunity_id")
    for old_name, new_name in INDEX_RENAMES_UP:
        _rename_index(old_name, new_name)


def downgrade() -> None:
    for old_name, new_name in reversed(INDEX_RENAMES_UP):
        _rename_index(new_name, old_name)
    for table_name in reversed(ROLE_ID_TABLES):
        op.alter_column(table_name, "opportunity_id", new_column_name="role_id")
    op.rename_table("opportunities", "roles")
