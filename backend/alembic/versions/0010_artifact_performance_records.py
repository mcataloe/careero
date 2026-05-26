"""artifact performance records

Revision ID: 0010_artifact_perf
Revises: 0009_application_notes_links
Create Date: 2026-05-18
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0010_artifact_perf"
down_revision = "0009_application_notes_links"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "artifact_performance_records",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("artifact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("artifact_type", sa.String(length=100), nullable=False),
        sa.Column("variant_name", sa.String(length=255), nullable=False),
        sa.Column("version_label", sa.String(length=100), nullable=True),
        sa.Column("targeted_role_category", sa.String(length=100), nullable=True),
        sa.Column("application_state_when_used", sa.String(length=100), nullable=True),
        sa.Column("response_outcome", sa.String(length=100), nullable=True),
        sa.Column("interview_outcome", sa.String(length=100), nullable=True),
        sa.Column("recruiter_engagement_outcome", sa.String(length=100), nullable=True),
        sa.Column(
            "compass_alignment",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
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
    op.create_index(
        "ix_artifact_performance_records_user_id",
        "artifact_performance_records",
        ["user_id"],
    )
    op.create_index(
        "ix_artifact_performance_records_workspace_id",
        "artifact_performance_records",
        ["workspace_id"],
    )
    op.create_index(
        "ix_artifact_performance_records_role_id",
        "artifact_performance_records",
        ["role_id"],
    )
    op.create_index(
        "ix_artifact_performance_records_application_id",
        "artifact_performance_records",
        ["application_id"],
    )
    op.create_index(
        "ix_artifact_performance_records_artifact_id",
        "artifact_performance_records",
        ["artifact_id"],
    )
    op.create_index(
        "ix_artifact_performance_records_artifact_type",
        "artifact_performance_records",
        ["artifact_type"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_artifact_performance_records_artifact_type",
        table_name="artifact_performance_records",
    )
    op.drop_index(
        "ix_artifact_performance_records_artifact_id",
        table_name="artifact_performance_records",
    )
    op.drop_index(
        "ix_artifact_performance_records_application_id",
        table_name="artifact_performance_records",
    )
    op.drop_index(
        "ix_artifact_performance_records_role_id",
        table_name="artifact_performance_records",
    )
    op.drop_index(
        "ix_artifact_performance_records_workspace_id",
        table_name="artifact_performance_records",
    )
    op.drop_index(
        "ix_artifact_performance_records_user_id",
        table_name="artifact_performance_records",
    )
    op.drop_table("artifact_performance_records")
