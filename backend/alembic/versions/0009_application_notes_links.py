"""application notes and external links

Revision ID: 0009_application_notes_links
Revises: 0008_application_workflow
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0009_application_notes_links"
down_revision = "0008_application_workflow"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "application_notes",
        sa.Column(
            "note_type",
            sa.String(length=100),
            server_default="general",
            nullable=False,
        ),
    )
    op.add_column(
        "application_notes",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "application_external_links",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_application_notes_deleted_at",
        "application_notes",
        ["deleted_at"],
    )
    op.create_index(
        "ix_application_notes_note_type",
        "application_notes",
        ["note_type"],
    )
    op.create_index(
        "ix_application_external_links_deleted_at",
        "application_external_links",
        ["deleted_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_application_external_links_deleted_at",
        table_name="application_external_links",
    )
    op.drop_index("ix_application_notes_note_type", table_name="application_notes")
    op.drop_index("ix_application_notes_deleted_at", table_name="application_notes")
    op.drop_column("application_external_links", "deleted_at")
    op.drop_column("application_notes", "deleted_at")
    op.drop_column("application_notes", "note_type")
