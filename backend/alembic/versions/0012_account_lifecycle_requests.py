"""account lifecycle requests

Revision ID: 0012_account_lifecycle_requests
Revises: 0011_automation_guardrails
Create Date: 2026-05-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0012_account_lifecycle_requests"
down_revision = "0011_automation_guardrails"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "account_lifecycle_requests",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_type", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            sa.String(length=100),
            server_default="requested",
            nullable=False,
        ),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("request_reason", sa.Text(), nullable=True),
        sa.Column("target_type", sa.String(length=100), nullable=True),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "request_metadata",
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_account_lifecycle_requests_user_id",
        "account_lifecycle_requests",
        ["user_id"],
    )
    op.create_index(
        "ix_account_lifecycle_requests_status",
        "account_lifecycle_requests",
        ["status"],
    )
    op.create_index(
        "ix_account_lifecycle_requests_user_status",
        "account_lifecycle_requests",
        ["user_id", "status"],
    )
    op.create_index(
        "ix_account_lifecycle_requests_type",
        "account_lifecycle_requests",
        ["request_type"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_account_lifecycle_requests_type",
        table_name="account_lifecycle_requests",
    )
    op.drop_index(
        "ix_account_lifecycle_requests_user_status",
        table_name="account_lifecycle_requests",
    )
    op.drop_index(
        "ix_account_lifecycle_requests_status",
        table_name="account_lifecycle_requests",
    )
    op.drop_index(
        "ix_account_lifecycle_requests_user_id",
        table_name="account_lifecycle_requests",
    )
    op.drop_table("account_lifecycle_requests")
