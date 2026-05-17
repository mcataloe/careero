"""application reminders lifecycle fields

Revision ID: 0010_application_reminders
Revises: 0009_application_notes_links
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0010_application_reminders"
down_revision = "0009_application_notes_links"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "application_reminders",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "application_reminders",
        sa.Column(
            "reminder_type",
            sa.String(length=100),
            server_default="follow_up",
            nullable=False,
        ),
    )
    op.add_column(
        "application_reminders",
        sa.Column(
            "priority",
            sa.String(length=50),
            server_default="normal",
            nullable=False,
        ),
    )
    op.add_column(
        "application_reminders",
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_application_reminders_deleted_at",
        "application_reminders",
        ["deleted_at"],
    )
    op.create_index(
        "ix_application_reminders_type",
        "application_reminders",
        ["reminder_type"],
    )
    op.create_index(
        "ix_application_reminders_priority",
        "application_reminders",
        ["priority"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_application_reminders_priority", table_name="application_reminders"
    )
    op.drop_index("ix_application_reminders_type", table_name="application_reminders")
    op.drop_index(
        "ix_application_reminders_deleted_at", table_name="application_reminders"
    )
    op.drop_column("application_reminders", "metadata")
    op.drop_column("application_reminders", "priority")
    op.drop_column("application_reminders", "reminder_type")
    op.drop_column("application_reminders", "deleted_at")
