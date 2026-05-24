"""automation guardrails

Revision ID: 0011_automation_guardrails
Revises: 0010_artifact_perf, 0010_interview_tracking
Create Date: 2026-05-24
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0011_automation_guardrails"
down_revision = ("0010_artifact_perf", "0010_interview_tracking")
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "automation_suggestions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_type", sa.String(length=100), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action_type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("basis", sa.Text(), nullable=False),
        sa.Column("confidence", sa.String(length=100), nullable=False),
        sa.Column(
            "source_inputs",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "preview",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("preview_hash", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            sa.String(length=100),
            server_default="active",
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("policy_version", sa.String(length=100), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"]),
        sa.ForeignKeyConstraint(["artifact_id"], ["generated_artifacts.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_automation_suggestions_user_id", "automation_suggestions", ["user_id"])
    op.create_index("ix_automation_suggestions_workspace_id", "automation_suggestions", ["workspace_id"])
    op.create_index(
        "ix_automation_suggestions_target",
        "automation_suggestions",
        ["target_type", "target_id"],
    )
    op.create_index(
        "ix_automation_suggestions_action_type",
        "automation_suggestions",
        ["action_type"],
    )
    op.create_index("ix_automation_suggestions_status", "automation_suggestions", ["status"])
    op.create_index(
        "ix_automation_suggestions_application_id",
        "automation_suggestions",
        ["application_id"],
    )
    op.create_index("ix_automation_suggestions_role_id", "automation_suggestions", ["role_id"])
    op.create_index(
        "ix_automation_suggestions_artifact_id",
        "automation_suggestions",
        ["artifact_id"],
    )

    op.create_table(
        "automation_approval_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("suggestion_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor", sa.String(length=100), nullable=False),
        sa.Column("target_type", sa.String(length=100), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_type", sa.String(length=100), nullable=False),
        sa.Column(
            "preview",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("preview_hash", sa.String(length=100), nullable=False),
        sa.Column("approval_status", sa.String(length=100), nullable=False),
        sa.Column("dismissal_or_rejection_reason", sa.Text(), nullable=True),
        sa.Column("execution_status", sa.String(length=100), nullable=False),
        sa.Column(
            "execution_result",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "external_mutation",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("policy_version", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["suggestion_id"], ["automation_suggestions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_automation_approval_logs_user_id", "automation_approval_logs", ["user_id"])
    op.create_index(
        "ix_automation_approval_logs_workspace_id",
        "automation_approval_logs",
        ["workspace_id"],
    )
    op.create_index(
        "ix_automation_approval_logs_suggestion_id",
        "automation_approval_logs",
        ["suggestion_id"],
    )
    op.create_index(
        "ix_automation_approval_logs_target",
        "automation_approval_logs",
        ["target_type", "target_id"],
    )
    op.create_index(
        "ix_automation_approval_logs_action_type",
        "automation_approval_logs",
        ["action_type"],
    )
    op.create_index(
        "ix_automation_approval_logs_approval_status",
        "automation_approval_logs",
        ["approval_status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_automation_approval_logs_approval_status",
        table_name="automation_approval_logs",
    )
    op.drop_index(
        "ix_automation_approval_logs_action_type",
        table_name="automation_approval_logs",
    )
    op.drop_index("ix_automation_approval_logs_target", table_name="automation_approval_logs")
    op.drop_index(
        "ix_automation_approval_logs_suggestion_id",
        table_name="automation_approval_logs",
    )
    op.drop_index(
        "ix_automation_approval_logs_workspace_id",
        table_name="automation_approval_logs",
    )
    op.drop_index("ix_automation_approval_logs_user_id", table_name="automation_approval_logs")
    op.drop_table("automation_approval_logs")

    op.drop_index("ix_automation_suggestions_artifact_id", table_name="automation_suggestions")
    op.drop_index("ix_automation_suggestions_role_id", table_name="automation_suggestions")
    op.drop_index(
        "ix_automation_suggestions_application_id",
        table_name="automation_suggestions",
    )
    op.drop_index("ix_automation_suggestions_status", table_name="automation_suggestions")
    op.drop_index(
        "ix_automation_suggestions_action_type",
        table_name="automation_suggestions",
    )
    op.drop_index("ix_automation_suggestions_target", table_name="automation_suggestions")
    op.drop_index("ix_automation_suggestions_workspace_id", table_name="automation_suggestions")
    op.drop_index("ix_automation_suggestions_user_id", table_name="automation_suggestions")
    op.drop_table("automation_suggestions")
