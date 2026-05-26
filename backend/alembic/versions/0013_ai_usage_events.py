"""ai usage events

Revision ID: 0013_ai_usage_events
Revises: 0012_account_lifecycle_requests
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0013_ai_usage_events"
down_revision = "0012_account_lifecycle_requests"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_usage_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("feature", sa.String(length=100), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=100), nullable=False),
        sa.Column("prompt_version", sa.String(length=100), nullable=True),
        sa.Column("ruleset_version", sa.String(length=100), nullable=True),
        sa.Column("input_token_estimate", sa.Integer(), nullable=True),
        sa.Column("output_token_estimate", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("error_class", sa.String(length=200), nullable=True),
        sa.Column("content_hash", sa.String(length=100), nullable=True),
        sa.Column(
            "event_metadata",
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
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"]),
        sa.ForeignKeyConstraint(["artifact_id"], ["generated_artifacts.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_usage_events_user_id", "ai_usage_events", ["user_id"])
    op.create_index(
        "ix_ai_usage_events_workspace_id",
        "ai_usage_events",
        ["workspace_id"],
    )
    op.create_index("ix_ai_usage_events_role_id", "ai_usage_events", ["role_id"])
    op.create_index("ix_ai_usage_events_feature", "ai_usage_events", ["feature"])
    op.create_index(
        "ix_ai_usage_events_event_type",
        "ai_usage_events",
        ["event_type"],
    )
    op.create_index("ix_ai_usage_events_created_at", "ai_usage_events", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_ai_usage_events_created_at", table_name="ai_usage_events")
    op.drop_index("ix_ai_usage_events_event_type", table_name="ai_usage_events")
    op.drop_index("ix_ai_usage_events_feature", table_name="ai_usage_events")
    op.drop_index("ix_ai_usage_events_role_id", table_name="ai_usage_events")
    op.drop_index("ix_ai_usage_events_workspace_id", table_name="ai_usage_events")
    op.drop_index("ix_ai_usage_events_user_id", table_name="ai_usage_events")
    op.drop_table("ai_usage_events")
